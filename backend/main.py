"""
FastAPI application entry point.
All routers are registered here; CORS and startup hooks are configured.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import create_tables
from app.api import (
    auth_router, upload_router, query_router,
    history_router, analytics_router, user_router,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup (idempotent via CREATE IF NOT EXISTS)."""
    logger.info("Starting up — creating database tables...")
    create_tables()
    logger.info("Database ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="AI-Powered Intelligent Query Resolution System — Phase 1",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(upload_router, prefix=API_PREFIX)
app.include_router(query_router, prefix=API_PREFIX)
app.include_router(history_router, prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)
app.include_router(user_router, prefix=API_PREFIX)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
