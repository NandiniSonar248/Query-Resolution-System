"""
Retriever — two-stage retrieval pipeline:

Stage 1 (Vector Search):
    Embed query → ChromaDB cosine search → get RERANKER_CANDIDATES chunks (e.g. 20)

Stage 2 (Cross-Encoder Re-Ranking, optional):
    Pass all (query, chunk) pairs to a lightweight Cross-Encoder model.
    The model looks at query + chunk together and scores real relevance.
    Keep only RETRIEVAL_TOP_K best (e.g. 5) after re-ranking.

If RERANKER_ENABLED = False in .env, Stage 2 is skipped and we return
top RETRIEVAL_TOP_K by vector similarity only (original behaviour).
"""
import logging
from typing import List, Dict, Any, Optional

from app.rag.embeddings import embed_query
from app.rag.vector_store import query_chunks
from app.core.config import settings

logger = logging.getLogger(__name__)


def retrieve(
    query: str,
    top_k: int = None,
    similarity_threshold: float = None,
    document_ids: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """
    Embed the query, retrieve candidates, optionally re-rank, and return
    the best top_k chunks above the similarity threshold.

    Returns:
        {
            "chunks":               list of chunk dicts (sorted best-first),
            "retrieval_confidence": float in [0, 1]
        }
    """
    final_top_k = top_k or settings.RETRIEVAL_TOP_K
    threshold = similarity_threshold if similarity_threshold is not None else settings.SIMILARITY_THRESHOLD

    # ── Stage 1: Vector Search ────────────────────────────────────────────────
    # If re-ranking is ON, fetch more candidates so the re-ranker has enough
    # to work with. Otherwise just fetch the final amount directly.
    candidates_k = settings.RERANKER_CANDIDATES if settings.RERANKER_ENABLED else final_top_k

    query_vec = embed_query(query)
    raw_chunks = query_chunks(query_vec, top_k=candidates_k, document_ids=document_ids)

    # Filter chunks below similarity threshold
    filtered = [c for c in raw_chunks if c["similarity_score"] >= threshold]
    filtered.sort(key=lambda c: c["similarity_score"], reverse=True)

    if not filtered:
        return {"chunks": [], "retrieval_confidence": 0.0}

    # ── Stage 2: Cross-Encoder Re-Ranking (optional) ──────────────────────────
    if settings.RERANKER_ENABLED and len(filtered) > 0:
        from app.rag.reranker import rerank
        best_chunks = rerank(query, filtered, top_k=final_top_k)
    else:
        best_chunks = filtered[:final_top_k]

    # ── Confidence Score ──────────────────────────────────────────────────────
    # Calculated from original vector similarity scores (stable, 0–1 range)
    retrieval_confidence = sum(c["similarity_score"] for c in best_chunks) / len(best_chunks)

    logger.info(
        f"Retrieval: {len(raw_chunks)} raw → {len(filtered)} above threshold "
        f"→ {len(best_chunks)} after re-rank | confidence={retrieval_confidence:.4f}"
    )

    return {
        "chunks": best_chunks,
        "retrieval_confidence": round(retrieval_confidence, 4),
    }
