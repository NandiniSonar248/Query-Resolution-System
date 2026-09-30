from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.schemas.query import QueryRequest, QueryResponse
from app.services.query_service import process_query
from app.services.user_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/query", tags=["Query"])

@router.post("", response_model=QueryResponse)
def handle_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a natural language query using the RAG pipeline.
    """
    try:
        result = process_query(request, current_user.id, db)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
