from sqlalchemy.orm import Session
from app.agents.orchestrator import orchestrator
from app.schemas.query import QueryRequest, CitationOut
from app.services.history_service import get_chat_history

def process_query(request: QueryRequest, user_id: int, db: Session) -> dict:
    """
    Run the LangGraph orchestrator on the user's query.
    Fetches chat history if session_id is provided, runs the agent graph,
    and returns the structured response.
    """
    
    # 1. Fetch chat history for multi-turn context
    chat_history = []
    if request.session_id:
        chat_history = get_chat_history(request.session_id, db, last_n=10)
        
    # 2. Initialize LangGraph state
    # Note: DB connection and IDs are passed in so the memory agent can save the interaction
    initial_state = {
        "query": request.query,
        "chat_history": chat_history,
        "session_id": request.session_id,
        "user_id": user_id,
        "db": db
    }
    
    # 3. Execute graph
    final_state = orchestrator.invoke(initial_state)
    
    # 4. Extract confidence
    r_conf = final_state.get("retrieval_confidence", 0.0)
    g_conf = final_state.get("generation_confidence", 0.0)
    overall_confidence = (r_conf + g_conf) / 2.0
    
    if overall_confidence > 0.8:
        conf_label = "High"
    elif overall_confidence > 0.5:
        conf_label = "Medium"
    else:
        conf_label = "Low"
        
    citations = []
    for c in final_state.get("citations", []):
        citations.append(CitationOut(
            chunk_id=c.get("chunk_id", ""),
            source_doc=c.get("source_doc", ""),
            excerpt="",
            similarity_score=r_conf
        ))
    
    # 5. Format final response
    return {
        "answer": final_state.get("answer_text") or "",
        "query_type": final_state.get("query_type", "unknown"),
        "confidence_score": overall_confidence,
        "confidence_label": conf_label,
        "citations": citations,
        "session_id": final_state.get("session_id", request.session_id or 0),
        "message_id": final_state.get("message_id", 0),
        "clarification_needed": final_state.get("clarification_needed", False),
        "clarifying_question": final_state.get("clarifying_question", None)
    }
