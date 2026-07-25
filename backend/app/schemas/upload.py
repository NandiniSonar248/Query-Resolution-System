from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentOut(BaseModel):
    id: int
    filename: str
    file_type: str
    upload_date: datetime
    chunk_count: int
    status: str

    class Config:
        from_attributes = True


class DocumentListOut(BaseModel):
    documents: List[DocumentOut]
    total: int


class UploadStatusOut(BaseModel):
    document_id: int
    filename: str
    status: str
    chunk_count: int
    message: str
