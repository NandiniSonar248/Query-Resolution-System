from typing import Dict, Any
from app.rag.retriever import retrieve

def retrieval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieval Agent LangGraph Node.
    
    Input state keys expected:
      - normalized_query (str): The context-resolved query from Query Understanding.
      
    Output state updates:
      - chunks (list): List of dicts containing retrieved chunk data.
      - retrieval_confidence (float): Average similarity score of retrieved chunks.
    """
    normalized_query = state.get("normalized_query", "")
    
    if not normalized_query:
        return {
            "chunks": [],
            "retrieval_confidence": 0.0
        }
        
    # retrieve() handles embedding the query, querying ChromaDB, 
    # filtering by threshold, and calculating retrieval_confidence.
    result = retrieve(query=normalized_query)
    
    return {
        "chunks": result["chunks"],
        "retrieval_confidence": result["retrieval_confidence"]
    }
