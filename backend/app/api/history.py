"""
History API — endpoints for managing chat sessions and viewing message history.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.models.user import User
from app.schemas.query import SessionOut, MessageOut
from app.services.user_service import get_current_user
from app.services.history_service import (
    get_sessions,
    get_session,
    create_session,
    delete_session,
)

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/sessions", response_model=List[SessionOut])
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all chat sessions for the current user."""
    sessions = get_sessions(current_user.id, db)
    return sessions


@router.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def new_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new chat session."""
    session = create_session(current_user.id, db)
    return session


@router.get("/sessions/{session_id}", response_model=SessionOut)
def get_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a session with all its messages."""
    session = get_session(session_id, current_user.id, db)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a chat session and all its messages."""
    deleted = delete_session(session_id, current_user.id, db)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
