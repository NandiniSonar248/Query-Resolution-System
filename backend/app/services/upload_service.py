"""
Upload Service — orchestrates the full ingestion pipeline for a single file.
Runs synchronously for now; can be moved to a background task (Celery/ARQ) later.
"""
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.document import Document
from app.models.user import User
from app.rag.loader import load_document
from app.rag.chunker import chunk_documents
from app.rag.embeddings import embed_texts
from app.rag.vector_store import add_chunks, delete_document_chunks
from app.core.config import settings

logger = logging.getLogger(__name__)


def _validate_file(filename: str, size_bytes: int) -> None:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File type '.{ext}' not allowed. Accepted: {settings.ALLOWED_EXTENSIONS}",
        )
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit.",
        )


def ingest_document(
    file_bytes: bytes,
    filename: str,
    user_id: int,
    doc_id: int,
) -> None:
    """
    Background task:
    1. Load → 2. Chunk → 3. Embed → 4. Store in ChromaDB → 5. Update DB record (ready)
    """
    from app.core.db import SessionLocal
    db = SessionLocal()
    
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        db.close()
        return

    try:
        logger.info(f"Loading document '{filename}' (doc_id={doc.id})")
        pages = load_document(file_bytes, filename)

        logger.info(f"Chunking {len(pages)} pages")
        chunks = chunk_documents(pages)
        logger.info(f"Created {len(chunks)} chunks")

        if not chunks:
            raise ValueError("No text content extracted from document.")

        logger.info("Generating embeddings...")
        texts = [c["text"] for c in chunks]
        embeddings = embed_texts(texts)

        logger.info(f"Storing {len(chunks)} chunks in vector store")
        stored = add_chunks(chunks, embeddings, doc.id)

        doc.chunk_count = stored
        doc.status = "ready"
        db.commit()
        logger.info(f"Ingestion complete: doc_id={doc.id}, chunks={stored}")

    except Exception as e:
        logger.error(f"Ingestion failed for doc_id={doc_id}: {e}")
        doc.status = "error"
        doc.error_message = str(e)[:512]
        db.commit()
    finally:
        db.close()


def list_documents(user: User, db: Session):
    return db.query(Document).filter(Document.user_id == user.id).all()


def delete_document(doc_id: int, user: User, db: Session) -> None:
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    delete_document_chunks(doc_id)
    db.delete(doc)
    db.commit()
