"""
Re-Ranker — Cross-Encoder based re-ranking for RAG retrieval quality.

How it works:
  1. The Retrieval Agent fetches RERANKER_CANDIDATES (e.g. 20) chunks from ChromaDB.
  2. This module passes every (query, chunk) pair through a lightweight Cross-Encoder model.
  3. The Cross-Encoder looks at both query AND chunk together and scores their relevance.
  4. We return only the top RETRIEVAL_TOP_K (e.g. 5) chunks sorted by re-rank score.

Why it's better than vector search alone:
  - Vector search finds "mathematically similar" text.
  - Cross-Encoder re-ranking finds "actually relevant to THIS specific question" text.
  - Model: cross-encoder/ms-marco-MiniLM-L-6-v2 (~25 MB, runs on CPU in <1s for 20 chunks).

The model is downloaded once from HuggingFace on first use and cached locally.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Singleton: load the model once and reuse across all requests
_cross_encoder = None


def _get_cross_encoder():
    """Lazy-load the cross-encoder model (downloads ~25 MB on first call)."""
    global _cross_encoder
    if _cross_encoder is None:
        try:
            from sentence_transformers import CrossEncoder
            from app.core.config import settings
            logger.info(f"Loading re-ranker model: {settings.RERANKER_MODEL}")
            try:
                # Try loading from local cache first (prevents network ping crashes)
                _cross_encoder = CrossEncoder(settings.RERANKER_MODEL, local_files_only=True)
                logger.info("Re-ranker model loaded successfully from local cache.")
            except Exception:
                # If not in cache yet, allow it to download
                _cross_encoder = CrossEncoder(settings.RERANKER_MODEL, local_files_only=False)
                logger.info("Re-ranker model downloaded and loaded successfully.")
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Re-ranking disabled. "
                "Run: pip install sentence-transformers"
            )
            _cross_encoder = None
    return _cross_encoder


def rerank(query: str, chunks: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
    """
    Re-rank a list of retrieved chunks using a Cross-Encoder model.

    Args:
        query:   The user's normalized query string.
        chunks:  List of chunk dicts from ChromaDB (each has 'text', 'similarity_score', etc.)
        top_k:   How many top chunks to return after re-ranking.

    Returns:
        A list of the top_k best chunks, sorted by cross-encoder score (best first).
        Each chunk gains a new 'rerank_score' field for transparency.
        Falls back to original order if the model is unavailable.
    """
    if not chunks:
        return chunks

    model = _get_cross_encoder()

    # Graceful fallback: if model not available, just return top_k of original order
    if model is None:
        logger.warning("Re-ranker unavailable — returning top-K by vector similarity.")
        return chunks[:top_k]

    try:
        # Build (query, chunk_text) pairs for the cross-encoder
        pairs = [(query, c.get("text", "")) for c in chunks]

        # Score all pairs in one batch (fast even on CPU)
        scores = model.predict(pairs)

        # Attach rerank_score to each chunk
        for chunk, score in zip(chunks, scores):
            chunk["rerank_score"] = float(score)

        # Sort descending by rerank score and return top-K
        reranked = sorted(chunks, key=lambda c: c.get("rerank_score", 0.0), reverse=True)

        logger.info(
            f"Re-ranked {len(chunks)} candidates → keeping top {top_k}. "
            f"Top score: {reranked[0].get('rerank_score', 0):.4f}"
        )

        return reranked[:top_k]

    except Exception as e:
        logger.error(f"Re-ranking failed: {e}. Falling back to vector similarity order.")
        return chunks[:top_k]
