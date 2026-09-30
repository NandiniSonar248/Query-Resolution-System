"""
Embeddings interface — supports Gemini (default) and Ollama providers.

Set EMBEDDING_PROVIDER=gemini  in .env to use Google Gemini (recommended for production).
Set EMBEDDING_PROVIDER=ollama  in .env to use local/ngrok Ollama (local dev only).

To swap providers, only this file and .env need to change — no agent logic changes needed.
"""
from typing import List
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


# ── Public API ────────────────────────────────────────────────────────────────

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a batch of texts using the configured embedding provider."""
    if not texts:
        return []
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "gemini":
        return _gemini_embed_batch(texts)
    else:
        return _ollama_embed_batch(texts)


def embed_query(query: str) -> List[float]:
    """Embed a single query string."""
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "gemini":
        return _gemini_embed_batch([query])[0]
    else:
        return _ollama_embed_single(query)


# ── Gemini Provider ───────────────────────────────────────────────────────────

def _gemini_embed_batch(texts: List[str]) -> List[List[float]]:
    """
    Embed texts using Google Gemini gemini-embedding-001.
    Calls embed_content once per text (most reliable approach).
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise RuntimeError(
            "google-genai package not installed. "
            "Run: pip install google-genai"
        )

    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set in .env. "
            "Get a free key at https://aistudio.google.com/apikey"
        )

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    model = settings.GEMINI_EMBED_MODEL
    all_embeddings: List[List[float]] = []

    for i, text in enumerate(texts):
        try:
            result = client.models.embed_content(
                model=model,
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )
            all_embeddings.append(result.embeddings[0].values)
            if (i + 1) % 20 == 0:
                logger.info(f"Gemini: embedded {i + 1}/{len(texts)} chunks")
        except Exception as e:
            raise RuntimeError(
                f"Gemini embedding request failed: {e}. "
                f"Ensure GEMINI_API_KEY is valid and model '{model}' is accessible."
            ) from e

    return all_embeddings


# ── Ollama Provider ───────────────────────────────────────────────────────────

def _ollama_embed_batch(texts: List[str]) -> List[List[float]]:
    """Try Ollama batch API first, fall back to per-text requests."""
    import httpx

    # Try the newer batch API first (/api/embed)
    url = f"{settings.OLLAMA_BASE_URL}/api/embed"
    payload = {"model": settings.OLLAMA_EMBED_MODEL, "input": texts}
    headers = {"ngrok-skip-browser-warning": "true"}
    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=300.0)
        if resp.status_code == 200:
            return resp.json()["embeddings"]
    except Exception:
        pass

    # Fallback: parallel per-text requests (/api/embeddings)
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        vectors = list(executor.map(_ollama_embed_single, texts))
    return vectors


def _ollama_embed_single(text: str) -> List[float]:
    import httpx

    url = f"{settings.OLLAMA_BASE_URL}/api/embeddings"
    payload = {"model": settings.OLLAMA_EMBED_MODEL, "prompt": text}
    headers = {"ngrok-skip-browser-warning": "true"}
    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=60.0)
        resp.raise_for_status()
        return resp.json()["embedding"]
    except httpx.HTTPError as e:
        raise RuntimeError(
            f"Ollama embedding request failed: {e}. "
            f"Ensure Ollama is running at {settings.OLLAMA_BASE_URL} "
            f"and model '{settings.OLLAMA_EMBED_MODEL}' is pulled."
        ) from e
