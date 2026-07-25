"""
Central application configuration.
All tuneable values are loaded from environment variables (with defaults).
No secrets or tunable values should be hardcoded elsewhere — import from here.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "AI Query Resolution System"
    DEBUG: bool = False

    # ── Database (SQLite default for local dev; swap SQLALCHEMY_DATABASE_URL
    #    to postgresql://... for Postgres) ────────────────────────────────────
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./app.db"

    # ── JWT ──────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── ChromaDB ──────────────────────────────────────────────────────────────
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_NAME: str = "document_chunks"
    # Set to "local" to use an embedded Chroma (no separate server needed for dev)
    CHROMA_MODE: str = "local"          # "local" | "http"
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # ── Ollama / LLM ─────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    OLLAMA_CHAT_MODEL: str = "llama3.1"

    # ── RAG pipeline tuning ──────────────────────────────────────────────────
    CHUNK_SIZE: int = 512              # characters per chunk
    CHUNK_OVERLAP: int = 64           # characters of overlap between chunks
    RETRIEVAL_TOP_K: int = 5          # how many chunks to retrieve
    SIMILARITY_THRESHOLD: float = 0.5  # minimum similarity score (0–1)

    # ── Upload limits ────────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list = ["pdf", "docx", "txt", "csv"]

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton — import and call this everywhere."""
    return Settings()


settings = get_settings()
