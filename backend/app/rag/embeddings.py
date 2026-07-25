"""
Embeddings interface backed by Ollama.

Design decision: All embedding calls go through this module.
To swap to OpenAI/another provider, replace the implementation of
`embed_texts()` and `embed_query()` here — no agent logic changes needed.
"""
from typing import List
import httpx
from app.core.config import settings


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed a batch of texts using the configured Ollama embedding model.
    Returns a list of float vectors in the same order as `texts`.
    """
    vectors: List[List[float]] = []
    # Ollama embedding API is per-prompt (no native batching in older versions)
    for text in texts:
        vec = _embed_single(text)
        vectors.append(vec)
    return vectors


def embed_query(query: str) -> List[float]:
    """Embed a single query string."""
    return _embed_single(query)


def _embed_single(text: str) -> List[float]:
    url = f"{settings.OLLAMA_BASE_URL}/api/embeddings"
    payload = {"model": settings.OLLAMA_EMBED_MODEL, "prompt": text}
    try:
        resp = httpx.post(url, json=payload, timeout=60.0)
        resp.raise_for_status()
        return resp.json()["embedding"]
    except httpx.HTTPError as e:
        raise RuntimeError(
            f"Ollama embedding request failed: {e}. "
            f"Ensure Ollama is running at {settings.OLLAMA_BASE_URL} "
            f"and model '{settings.OLLAMA_EMBED_MODEL}' is pulled."
        ) from e
