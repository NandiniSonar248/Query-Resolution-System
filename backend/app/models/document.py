from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.db import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(512), nullable=False)
    file_type = Column(String(16), nullable=False)   # pdf | docx | txt | csv
    upload_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    chunk_count = Column(Integer, default=0)
    # status: "pending" | "processing" | "ready" | "error"
    status = Column(String(32), default="pending", nullable=False)
    error_message = Column(Text, nullable=True)

    owner = relationship("User", back_populates="documents")
