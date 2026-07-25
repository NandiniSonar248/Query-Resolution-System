"""
SQLAlchemy database session factory.

Usage anywhere in the app:
    from app.core.db import get_db
    # FastAPI dependency:
    db: Session = Depends(get_db)
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# SQLite needs the connect_args fix for threading; Postgres does not.
_connect_args = (
    {"check_same_thread": False}
    if settings.SQLALCHEMY_DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    connect_args=_connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables defined in models. Called at startup."""
    # Import all model modules so that Base.metadata is populated
    from app.models import user, document, session  # noqa: F401
    Base.metadata.create_all(bind=engine)
