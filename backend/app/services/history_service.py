"""
History Service — CRUD operations for ChatSessions and Messages.

Provides the data layer for the Memory Agent and History API.
"""
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.session import ChatSession, Message


def get_sessions(user_id: int, db: Session) -> List[ChatSession]:
    """List all chat sessions for a user, newest first."""
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )


def get_session(session_id: int, user_id: int, db: Session) -> Optional[ChatSession]:
    """Get a single session with all its messages (ownership-checked)."""
    return (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )


def create_session(user_id: int, db: Session, title: str = "New Chat") -> ChatSession:
    """Create a new chat session."""
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def delete_session(session_id: int, user_id: int, db: Session) -> bool:
    """Delete a session and all its messages. Returns True if deleted."""
    session = get_session(session_id, user_id, db)
    if not session:
        return False
    db.delete(session)
    db.commit()
    return True


def add_message(
    session_id: int,
    role: str,
    content: str,
    db: Session,
    query_type: Optional[str] = None,
    confidence_score: Optional[float] = None,
    citations: Optional[list] = None,
) -> Message:
    """Add a message to a session."""
    msg = Message(
        session_id=session_id,
        role=role,
        content=content,
        query_type=query_type,
        confidence_score=confidence_score,
        citations_json=json.dumps(citations) if citations else None,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_chat_history(session_id: int, db: Session, last_n: int = 10) -> List[dict]:
    """
    Fetch the last N messages from a session as a list of
    {'role': 'user'|'assistant', 'content': '...'} dicts.
    Used by the orchestrator for multi-turn context.
    """
    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(last_n)
        .all()
    )
    # Reverse to get chronological order
    messages.reverse()
    return [{"role": m.role, "content": m.content} for m in messages]


def update_session_title(session_id: int, title: str, db: Session) -> None:
    """Update a session's title (e.g., based on first user query)."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session:
        session.title = title[:256]  # max length from model
        db.commit()
