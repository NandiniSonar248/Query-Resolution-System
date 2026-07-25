"""
Document Loader — handles PDF, DOCX, TXT, and CSV files.
Returns a list of (text, metadata) tuples where metadata carries the
source filename and page/section info for later citation.
"""
import csv
import io
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Optional heavy imports — fail fast with a clear message if not installed
try:
    import fitz  # PyMuPDF
    _PDF_AVAILABLE = True
except ImportError:
    _PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    _DOCX_AVAILABLE = True
except ImportError:
    _DOCX_AVAILABLE = False


PagedContent = List[Tuple[str, Dict[str, Any]]]


def load_document(file_bytes: bytes, filename: str) -> PagedContent:
    """
    Load a document from raw bytes.

    Returns:
        List of (text_chunk, metadata) where metadata contains:
            - source_doc: original filename
            - page: page number or section index (1-based)
    """
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext == "pdf":
        return _load_pdf(file_bytes, filename)
    elif ext == "docx":
        return _load_docx(file_bytes, filename)
    elif ext == "txt":
        return _load_txt(file_bytes, filename)
    elif ext == "csv":
        return _load_csv(file_bytes, filename)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _load_pdf(data: bytes, filename: str) -> PagedContent:
    if not _PDF_AVAILABLE:
        raise RuntimeError("PyMuPDF (fitz) not installed. Run: pip install pymupdf")
    result: PagedContent = []
    doc = fitz.open(stream=data, filetype="pdf")
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if text:
            result.append((text, {"source_doc": filename, "page": page_num}))
    doc.close()
    return result


def _load_docx(data: bytes, filename: str) -> PagedContent:
    if not _DOCX_AVAILABLE:
        raise RuntimeError("python-docx not installed. Run: pip install python-docx")
    doc = DocxDocument(io.BytesIO(data))
    # Group paragraphs into logical sections (split on Heading styles)
    sections: PagedContent = []
    current_text: List[str] = []
    section_idx = 1
    for para in doc.paragraphs:
        if para.style.name.startswith("Heading") and current_text:
            sections.append(
                ("\n".join(current_text).strip(), {"source_doc": filename, "page": section_idx})
            )
            current_text = [para.text]
            section_idx += 1
        else:
            if para.text.strip():
                current_text.append(para.text.strip())
    if current_text:
        sections.append(
            ("\n".join(current_text).strip(), {"source_doc": filename, "page": section_idx})
        )
    return sections if sections else [(" ".join([p.text for p in doc.paragraphs]),
                                       {"source_doc": filename, "page": 1})]


def _load_txt(data: bytes, filename: str) -> PagedContent:
    text = data.decode("utf-8", errors="replace")
    return [(text, {"source_doc": filename, "page": 1})]


def _load_csv(data: bytes, filename: str) -> PagedContent:
    """Convert CSV rows to prose text: 'Column: value, Column2: value2' per row."""
    result: PagedContent = []
    text = data.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    for idx, row in enumerate(reader, start=1):
        prose = ", ".join(f"{k}: {v}" for k, v in row.items() if v)
        if prose:
            result.append((prose, {"source_doc": filename, "page": idx}))
    return result
