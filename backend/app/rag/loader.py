"""
Document Loader — handles PDF, DOCX, TXT, and CSV files.
Supports structured Table-to-Markdown extraction for both PDF and DOCX,
ensuring tables, marksheets, spreadsheets, and tabular data are fully preserved.
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
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table as DocxTable
    from docx.text.paragraph import Paragraph as DocxParagraph
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
    """
    Extract text and structured tables from PDF.
    Uses PyMuPDF's page.find_tables() to convert tables into clean Markdown.
    """
    if not _PDF_AVAILABLE:
        raise RuntimeError("PyMuPDF (fitz) not installed. Run: pip install pymupdf")

    result: PagedContent = []
    doc = fitz.open(stream=data, filetype="pdf")

    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text().strip()

        # Extract structured tables via PyMuPDF table finder
        md_tables = []
        try:
            tabs = page.find_tables()
            for tab in tabs:
                try:
                    md = tab.to_markdown()
                    if md and md.strip():
                        md_tables.append(md.strip())
                except Exception:
                    pass
        except Exception:
            pass  # Fall back to raw text if table extraction fails on this page

        # Combine narrative text with structured tables
        content_parts = []
        if page_text:
            content_parts.append(page_text)
        if md_tables:
            content_parts.append("\n\n### Extracted Tables:\n" + "\n\n".join(md_tables))

        full_page_content = "\n\n".join(content_parts).strip()
        if full_page_content:
            result.append((full_page_content, {"source_doc": filename, "page": page_num}))

    doc.close()

    # Fallback: try pdfplumber if PyMuPDF extracted nothing (e.g. scanned PDFs)
    if not result:
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = (page.extract_text() or "").strip()
                    # Also extract tables via pdfplumber
                    try:
                        extracted_tables = page.extract_tables()
                        for t in extracted_tables:
                            if t and len(t) > 1:
                                header = "| " + " | ".join(str(c or '').strip().replace('\n', ' ') for c in t[0]) + " |"
                                sep = "| " + " | ".join(["---"] * len(t[0])) + " |"
                                rows = ["| " + " | ".join(str(c or '').strip().replace('\n', ' ') for c in r) + " |" for r in t[1:]]
                                text += f"\n\n{header}\n{sep}\n" + "\n".join(rows)
                    except Exception:
                        pass
                    if text:
                        result.append((text, {"source_doc": filename, "page": page_num}))
        except Exception:
            pass

    if not result:
        raise ValueError(
            "No text content extracted from this PDF. "
            "It may be a scanned image-only PDF with no selectable text. "
            "Please use a PDF with actual text content."
        )
    return result


def _docx_table_to_markdown(table: DocxTable) -> str:
    """Convert a python-docx Table object into a clean Markdown table."""
    rows: List[List[str]] = []
    for r in table.rows:
        row_cells: List[str] = []
        for c in r.cells:
            text = c.text.strip().replace("\n", " ")
            # Deduplicate merged cells that appear repeatedly in the row
            if not row_cells or text != row_cells[-1]:
                row_cells.append(text)
        if any(row_cells):
            rows.append(row_cells)

    if not rows:
        return ""

    num_cols = len(rows[0])
    # Pad shorter rows if any
    for r in rows:
        while len(r) < num_cols:
            r.append("")

    header = "| " + " | ".join(rows[0]) + " |"
    separator = "| " + " | ".join(["---"] * num_cols) + " |"
    body = "\n".join("| " + " | ".join(r[:num_cols]) + " |" for r in rows[1:])

    return f"\n{header}\n{separator}\n{body}\n"


def _load_docx(data: bytes, filename: str) -> PagedContent:
    """
    Extract text and tables from Word (.docx) documents in true reading order.
    Converts tables directly to clean Markdown.
    """
    if not _DOCX_AVAILABLE:
        raise RuntimeError("python-docx not installed. Run: pip install python-docx")

    doc = DocxDocument(io.BytesIO(data))
    sections: PagedContent = []
    current_elements: List[str] = []
    section_idx = 1

    # Traverse document body in exact visual order (paragraphs & tables interleaved)
    for child in doc.element.body.iterchildren():
        if isinstance(child, CT_P):
            p = DocxParagraph(child, doc)
            text = p.text.strip()
            if not text:
                continue

            # Split section on Heading styles
            if p.style.name.startswith("Heading") and current_elements:
                sections.append(
                    ("\n".join(current_elements).strip(), {"source_doc": filename, "page": section_idx})
                )
                current_elements = [text]
                section_idx += 1
            else:
                current_elements.append(text)

        elif isinstance(child, CT_Tbl):
            # Extract table as formatted Markdown
            md_table = _docx_table_to_markdown(DocxTable(child, doc))
            if md_table.strip():
                current_elements.append(md_table)

    if current_elements:
        sections.append(
            ("\n".join(current_elements).strip(), {"source_doc": filename, "page": section_idx})
        )

    return sections if sections else [("", {"source_doc": filename, "page": 1})]


def _load_txt(data: bytes, filename: str) -> PagedContent:
    text = data.decode("utf-8", errors="replace")
    return [(text, {"source_doc": filename, "page": 1})]


def _load_csv(data: bytes, filename: str) -> PagedContent:
    """Convert CSV rows to structured prose: 'Column: value, Column2: value2' per row."""
    result: PagedContent = []
    text = data.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    for idx, row in enumerate(reader, start=1):
        prose = ", ".join(f"{k}: {v}" for k, v in row.items() if v)
        if prose:
            result.append((prose, {"source_doc": filename, "page": idx}))
    return result
