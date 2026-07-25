from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.db import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(256), default="New Chat")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan",
                            order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    # role: "user" | "assistant" | "clarification"
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    # query_type: "factual" | "procedural" | "comparative" | "ambiguous" | null
    query_type = Column(String(32), nullable=True)
    confidence_score = Column(Float, nullable=True)
    citations_json = Column(Text, nullable=True)     # JSON string of citation list
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session = relationship("ChatSession", back_populates="messages")


class KnowledgeGapLog(Base):
    __tablename__ = "knowledge_gap_logs"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    query_type = Column(String(32), nullable=True)
    confidence_score = Column(Float, nullable=True)
    was_answered = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
