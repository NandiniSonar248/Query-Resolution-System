"""
Retriever — combines embedding + vector store query + threshold filtering.
This is the entry point for the Retrieval Agent in Phase 2.
"""
from typing import List, Dict, Any, Optional
from app.rag.embeddings import embed_query
from app.rag.vector_store import query_chunks
from app.core.config import settings


def retrieve(
    query: str,
    top_k: int = None,
    similarity_threshold: float = None,
    document_ids: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """
    Embed the query and retrieve top-K chunks above the similarity threshold.

    Returns:
        {
            "chunks": [...],           # filtered chunks sorted by similarity
            "retrieval_confidence":    # float in [0, 1]
        }
    """
    k = top_k or settings.RETRIEVAL_TOP_K
    threshold = similarity_threshold if similarity_threshold is not None else settings.SIMILARITY_THRESHOLD

    query_vec = embed_query(query)
    raw_chunks = query_chunks(query_vec, top_k=k, document_ids=document_ids)

    # Filter out low-confidence chunks
    filtered = [c for c in raw_chunks if c["similarity_score"] >= threshold]
    filtered.sort(key=lambda c: c["similarity_score"], reverse=True)

    # Retrieval confidence = average similarity of kept chunks (0 if none found)
    if filtered:
        retrieval_confidence = sum(c["similarity_score"] for c in filtered) / len(filtered)
    else:
        retrieval_confidence = 0.0

    return {
        "chunks": filtered,
        "retrieval_confidence": round(retrieval_confidence, 4),
    }
