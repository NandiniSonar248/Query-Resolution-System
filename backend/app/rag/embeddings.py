"""
Embeddings interface — supports Gemini (default) and Ollama providers.

Set EMBEDDING_PROVIDER=gemini  in .env to use Google Gemini (recommended for production).
Set EMBEDDING_PROVIDER=ollama  in .env to use local/ngrok Ollama (local dev only).

To swap providers, only this file and .env need to change — no agent logic changes needed.
"""
from typing import List, Optional
import logging
import random
import time

from app.core.config import settings

logger = logging.getLogger(__name__)


# ── Public API ────────────────────────────────────────────────────────────────

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a batch of texts using the configured embedding provider."""
    if not texts:
        return []
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "gemini":
        return _gemini_embed_batch(texts, task_type="RETRIEVAL_DOCUMENT")
    else:
        return _ollama_embed_batch(texts)


def embed_query(query: str) -> List[float]:
    """Embed a single query string."""
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "gemini":
        return _gemini_embed_batch([query], task_type="RETRIEVAL_QUERY")[0]
    else:
        return _ollama_embed_single(query)


# ── Gemini Provider ───────────────────────────────────────────────────────────

def _gemini_embed_batch(
    texts: List[str],
    task_type: str = "RETRIEVAL_DOCUMENT",
    batch_size: int = 20,
    max_retries: int = 4,
) -> List[List[float]]:
    """
    Embed texts using Google Gemini API (gemini-embedding-001).
    Batches texts (up to batch_size per request) and applies exponential
    backoff retry for transient network and 503/429/500 errors.
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

    def _call_with_retry(contents: List[str]) -> List[List[float]]:
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                result = client.models.embed_content(
                    model=model,
                    contents=contents,
                    config=types.EmbedContentConfig(task_type=task_type),
                )
                return [emb.values for emb in result.embeddings]
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                is_transient = (
                    "503" in err_str
                    or "unavailable" in err_str
                    or "429" in err_str
                    or "resource_exhausted" in err_str
                    or "rate" in err_str
                    or "500" in err_str
                    or "timeout" in err_str
                    or "connection" in err_str
                )
                if is_transient and attempt < max_retries:
                    delay = (2 ** attempt) + random.uniform(0.5, 1.5)
                    logger.warning(
                        f"Gemini embed temporary failure ({e}). Retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})..."
                    )
                    time.sleep(delay)
                else:
                    break
        raise last_error

    # Process in batches
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        try:
            batch_embeddings = _call_with_retry(batch)
            all_embeddings.extend(batch_embeddings)
            logger.info(f"Gemini: embedded {min(i + len(batch), len(texts))}/{len(texts)} chunks")
        except Exception as e:
            # If batch failed after retries, fallback to item-by-item processing
            logger.warning(f"Batch embedding failed ({e}); falling back to item-by-item with retry...")
            for text in batch:
                try:
                    single_emb = _call_with_retry([text])[0]
                    all_embeddings.append(single_emb)
                except Exception as single_err:
                    raise RuntimeError(
                        f"Gemini embedding request failed: {single_err}. "
                        f"Ensure GEMINI_API_KEY is valid and model '{model}' is accessible."
                    ) from single_err

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
