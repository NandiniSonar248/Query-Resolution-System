"""
Text Chunker — two strategies controlled by settings.SEMANTIC_CHUNKING_ENABLED:

1. SEMANTIC (default, recommended):
   Detects structural boundaries:
     - Markdown headings (#, ##, ###)
     - Numbered sections (1., 1.1, etc.)
     - All-caps section titles (e.g., AWARDS & ACHIEVEMENTS, TECHNICAL SKILLS)
     - Paragraph breaks
   Crucially, keeps the heading attached to the content so context is never lost.
   Chunks are complete logical sections rather than arbitrary character windows.

2. FIXED-WINDOW (legacy fallback):
   The original sliding window with character overlap.
   Used if SEMANTIC_CHUNKING_ENABLED = False in .env.
"""
import re
from typing import List, Tuple, Dict, Any
from app.core.config import settings

Chunk = Dict[str, Any]  # {text, source_doc, page, chunk_index}


def _is_heading(line: str) -> bool:
    """Return True if line appears to be a structural heading."""
    line = line.strip()
    if not line:
        return False
    # Markdown heading: # Header, ## Subheader
    if re.match(r'^#{1,6}\s+.+', line):
        return True
    # All-caps or Title-case section title (e.g., "AWARDS & ACHIEVEMENTS", "PROJECTS", "EDUCATION")
    if re.match(r'^[A-Z0-9][A-Z0-9\s&/\\:,-]{2,60}$', line) and len(line) <= 60:
        return True
    # Numbered major section: "1. Project Name", "2.1 Overview"
    if re.match(r'^\d+(\.\d+)*\s+[A-Z]', line) and len(line) <= 80:
        return True
    return False


def _split_into_sections(text: str) -> List[str]:
    """
    Split text into logical sections while keeping headings attached to the content.
    """
    max_chars = settings.SEMANTIC_CHUNK_MAX_CHARS

    # Normalize newlines and break into lines
    raw_lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not raw_lines:
        return []

    sections: List[str] = []
    current_chunk: List[str] = []
    current_len = 0

    for line in raw_lines:
        heading = _is_heading(line)

        # If we hit a new heading and already have some content, start a new chunk
        if heading and current_chunk and current_len >= 80:
            sections.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_len = len(line)
        else:
            # If adding this line would exceed max_chars, flush current chunk
            if current_len + len(line) + 1 > max_chars and current_chunk:
                sections.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_len = len(line)
            else:
                current_chunk.append(line)
                current_len += len(line) + 1

    if current_chunk:
        sections.append('\n'.join(current_chunk))

    return sections


def _semantic_chunk(
    pages: List[Tuple[str, Dict[str, Any]]]
) -> List[Chunk]:
    """Semantic chunking: split on structure, keep headings attached."""
    chunks: List[Chunk] = []
    chunk_idx = 0
    min_chars = settings.SEMANTIC_CHUNK_MIN_CHARS

    for text, meta in pages:
        text = text.strip()
        if not text:
            continue

        sections = _split_into_sections(text)
        for section in sections:
            section_clean = section.strip()
            if len(section_clean) < min_chars:
                continue
            chunks.append({
                "text": section_clean,
                "source_doc": meta.get("source_doc", "unknown"),
                "page": meta.get("page", 1),
                "chunk_index": chunk_idx,
            })
            chunk_idx += 1

    return chunks


def _fixed_window_chunk(
    pages: List[Tuple[str, Dict[str, Any]]],
    chunk_size: int,
    chunk_overlap: int,
) -> List[Chunk]:
    """Original sliding-window strategy kept as fallback."""
    chunks: List[Chunk] = []
    chunk_idx = 0

    for text, meta in pages:
        text = text.strip()
        if not text:
            continue
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            if end < len(text):
                for sep in ["\n\n", "\n", ". ", " "]:
                    idx = text.rfind(sep, max(start, end - 100), end)
                    if idx != -1:
                        end = idx + len(sep)
                        break

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "source_doc": meta.get("source_doc", "unknown"),
                    "page": meta.get("page", 1),
                    "chunk_index": chunk_idx,
                })
                chunk_idx += 1

            start = end - chunk_overlap if end - chunk_overlap > start else end

    return chunks


def chunk_documents(
    pages: List[Tuple[str, Dict[str, Any]]],
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> List[Chunk]:
    """
    Route to semantic or fixed-window chunking based on config.
    """
    if settings.SEMANTIC_CHUNKING_ENABLED:
        return _semantic_chunk(pages)
    else:
        size = chunk_size or settings.CHUNK_SIZE
        overlap = chunk_overlap or settings.CHUNK_OVERLAP
        return _fixed_window_chunk(pages, size, overlap)
