from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class QueryRequest(BaseModel):
    query: str
    session_id: Optional[int] = None


class CitationOut(BaseModel):
    chunk_id: str
    source_doc: str
    excerpt: str
    similarity_score: float


class QueryResponse(BaseModel):
    answer: str
    query_type: str
    confidence_score: float
    confidence_label: str      # "High" | "Medium" | "Low"
    citations: List[CitationOut]
    session_id: int
    message_id: int
    clarification_needed: bool = False
    clarifying_question: Optional[str] = None


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    query_type: Optional[str]
    confidence_score: Optional[float]
    citations_json: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SessionOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True
