from fastapi import APIRouter, Depends, UploadFile, File, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.services.user_service import get_current_user
from app.services.upload_service import ingest_document, list_documents, delete_document
from app.models.user import User
from app.models.document import Document
from app.schemas.upload import DocumentOut, DocumentListOut, UploadStatusOut

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("", response_model=UploadStatusOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload and ingest a document asynchronously."""
    file_bytes = await file.read()
    
    # Pre-create the document in DB with status "processing"
    from app.services.upload_service import _validate_file
    _validate_file(file.filename, len(file_bytes))
    
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_type=ext,
        status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Run the heavy processing in the background
    background_tasks.add_task(ingest_document, file_bytes, file.filename, current_user.id, doc.id)
    
    return UploadStatusOut(
        document_id=doc.id,
        filename=doc.filename,
        status=doc.status,
        chunk_count=0,
        message="Upload received, processing in background.",
    )


@router.get("", response_model=DocumentListOut)
def list_my_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all documents uploaded by the current user."""
    docs = list_documents(current_user, db)
    return DocumentListOut(
        documents=[DocumentOut.model_validate(d) for d in docs],
        total=len(docs),
    )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a document and its vector embeddings."""
    delete_document(doc_id, current_user, db)
