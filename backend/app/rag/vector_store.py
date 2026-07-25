"""
ChromaDB vector store interface.

Design decision (SPEC §11):
    CHROMA_MODE="local" uses a persistent on-disk embedded Chroma (no external
    process needed for dev/testing). Set CHROMA_MODE="http" to point at the
    Chroma container from docker-compose.

    Collection: "document_chunks"
    Stored metadata per chunk: document_id, source_doc, chunk_index, page
"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings


def _get_client() -> chromadb.Client:
    if settings.CHROMA_MODE == "http":
        return chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
        )
    else:
        # Local persistent mode — no external process required
        return chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)


def _get_collection() -> chromadb.Collection:
    client = _get_client()
    return client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},   # cosine similarity for embedding comparison
    )


def add_chunks(
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    document_id: int,
) -> int:
    """
    Store chunks + pre-computed embeddings in ChromaDB.
    Returns the number of chunks stored.
    """
    collection = _get_collection()
    ids: List[str] = []
    metadatas: List[Dict[str, Any]] = []
    documents: List[str] = []

    for chunk, vec in zip(chunks, embeddings):
        chunk_id = f"doc{document_id}_chunk{chunk['chunk_index']}"
        ids.append(chunk_id)
        documents.append(chunk["text"])
        metadatas.append({
            "document_id": str(document_id),
            "source_doc": chunk["source_doc"],
            "chunk_index": chunk["chunk_index"],
            "page": chunk["page"],
        })

    # Use upsert so re-ingesting a document is idempotent
    collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    return len(ids)


def query_chunks(
    query_embedding: List[float],
    top_k: int = None,
    document_ids: Optional[List[int]] = None,
) -> List[Dict[str, Any]]:
    """
    Semantic search. Returns a list of chunk dicts with similarity scores.
    Optionally filter to specific document IDs.
    """
    k = top_k or settings.RETRIEVAL_TOP_K
    collection = _get_collection()

    where_clause = None
    if document_ids:
        str_ids = [str(d) for d in document_ids]
        where_clause = {"document_id": {"$in": str_ids}}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where_clause,
        include=["documents", "metadatas", "distances"],
    )

    chunks_out: List[Dict[str, Any]] = []
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    for chunk_id, text, meta, dist in zip(ids, docs, metas, dists):
        # Chroma cosine distance: 0 = identical, 2 = opposite
        # Convert to similarity in [0, 1]
        similarity = max(0.0, 1.0 - (dist / 2.0))
        chunks_out.append({
            "chunk_id": chunk_id,
            "text": text,
            "source_doc": meta.get("source_doc", "unknown"),
            "page": meta.get("page", 1),
            "chunk_index": meta.get("chunk_index", 0),
            "document_id": meta.get("document_id"),
            "similarity_score": round(similarity, 4),
        })

    return chunks_out


def delete_document_chunks(document_id: int) -> None:
    """Remove all chunks associated with a document (e.g. on document deletion)."""
    collection = _get_collection()
    collection.delete(where={"document_id": str(document_id)})


def get_chunk_count(document_id: Optional[int] = None) -> int:
    """Return total number of stored chunks, optionally filtered by document."""
    collection = _get_collection()
    if document_id is not None:
        result = collection.get(where={"document_id": str(document_id)})
        return len(result["ids"])
    return collection.count()
