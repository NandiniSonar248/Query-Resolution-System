"""
Text Chunker — splits raw page/section text into overlapping chunks.

Design decision (SPEC §11):
    chunk_size=512 chars, overlap=64 chars by default.
    We chunk on character boundaries but try to break on sentence/paragraph
    boundaries first to keep chunks semantically coherent.
"""
from typing import List, Tuple, Dict, Any
from app.core.config import settings

Chunk = Dict[str, Any]  # {text, source_doc, page, chunk_index}


def chunk_documents(
    pages: List[Tuple[str, Dict[str, Any]]],
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> List[Chunk]:
    """
    Take a list of (text, metadata) pages and split them into overlapping chunks.
    Returns list of chunk dicts ready for embedding.
    """
    size = chunk_size or settings.CHUNK_SIZE
    overlap = chunk_overlap or settings.CHUNK_OVERLAP

    chunks: List[Chunk] = []
    chunk_idx = 0

    for text, meta in pages:
        text = text.strip()
        if not text:
            continue
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            # Try to break on a paragraph/sentence boundary
            if end < len(text):
                # Look for "\n\n", "\n", or ". " within the last 100 chars
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

            start = end - overlap if end - overlap > start else end

    return chunks
