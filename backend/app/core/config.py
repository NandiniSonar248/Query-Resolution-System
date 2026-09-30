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

    # ── Embedding provider ────────────────────────────────────────────────────
    # "gemini"  → Google Gemini API (recommended for production, free tier)
    # "ollama"  → Local / ngrok Ollama (local dev only)
    EMBEDDING_PROVIDER: str = "gemini"

    # ── Google Gemini ─────────────────────────────────────────────────────────
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_EMBED_MODEL: str = "gemini-embedding-001"   # embedding model
    GEMINI_CHAT_MODEL: str = "gemini-3.5-flash-lite"   # chat model (free: 1500 req/day)

    # ── Ollama / LLM ─────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    OLLAMA_CHAT_MODEL: str = "llama3.1"

    # ── RAG pipeline tuning ──────────────────────────────────────────────────
    CHUNK_SIZE: int = 512              # characters per chunk (used when semantic chunking is OFF)
    CHUNK_OVERLAP: int = 64           # characters of overlap between chunks
    RETRIEVAL_TOP_K: int = 5          # final chunks sent to LLM after re-ranking
    SIMILARITY_THRESHOLD: float = 0.5  # minimum similarity score (0–1)

    # ── Semantic Chunking ─────────────────────────────────────────────────────
    SEMANTIC_CHUNKING_ENABLED: bool = True
    SEMANTIC_CHUNK_MAX_CHARS: int = 1500   # max chars per semantic chunk before force-splitting
    SEMANTIC_CHUNK_MIN_CHARS: int = 30     # discard only truly tiny fragments (< 30 chars)

    # ── Re-Ranking (Cross-Encoder) ────────────────────────────────────────────
    RERANKER_ENABLED: bool = True
    RERANKER_CANDIDATES: int = 20          # pull this many from ChromaDB before re-ranking
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # ── Upload limits ────────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list = ["pdf", "docx", "txt", "csv"]

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    # ── ElevenLabs Speech ────────────────────────────────────────────────────
    SPEECH_ENABLED: bool = True
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_BASE_URL: str = "https://api.elevenlabs.io/v1"
    ELEVENLABS_STT_MODEL: str = "scribe_v2"
    ELEVENLABS_TTS_MODEL: str = "eleven_flash_v2_5"
    ELEVENLABS_VOICE_ID: str = "bfGb7JTLUnZebZRiFYyq"
    ELEVENLABS_TTS_OUTPUT_FORMAT: str = "mp3_44100_128"
    SPEECH_MAX_UPLOAD_MB: int = 25
    SPEECH_MAX_TTS_CHARS: int = 5000
    SPEECH_REQUEST_TIMEOUT_SECONDS: int = 120

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton — import and call this everywhere."""
    return Settings()


settings = get_settings()
