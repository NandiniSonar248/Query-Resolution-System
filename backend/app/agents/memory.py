from typing import Dict, Any
from app.services.history_service import create_session, update_session_title, add_message
from app.models.session import KnowledgeGapLog

# Confidence threshold below which a query is flagged as a knowledge gap
KNOWLEDGE_GAP_THRESHOLD = 0.75

def memory_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Memory Agent LangGraph Node.
    
    Runs at the end of the query pipeline.
    1. Persists the user's query and assistant's response to the database.
    2. Logs low-confidence or unanswered queries to knowledge_gap_logs.
    """
    db = state.get("db")
    user_id = state.get("user_id")
    session_id = state.get("session_id")
    query = state.get("query", "")
    answer = state.get("answer_text") or state.get("clarifying_question") or ""
    query_type = state.get("query_type")
    
    # Calculate confidence to save
    r_conf = state.get("retrieval_confidence", 0.0)
    g_conf = state.get("generation_confidence", 0.0)
    overall_conf = (r_conf + g_conf) / 2.0
    
    citations = state.get("citations", [])
    is_clarification = state.get("clarification_needed", False)
    
    # Skip saving if we don't have db access
    if not db or not user_id:
        return state
        
    # 1. Ensure we have a session
    is_new_session = False
    if not session_id:
        session = create_session(user_id, db)
        session_id = session.id
        is_new_session = True
        
    # 2. Save User Message
    add_message(
        session_id=session_id,
        role="user",
        content=query,
        db=db,
        query_type=query_type
    )
    
    # 3. Save Assistant Message (or clarification question)
    role = "clarification" if is_clarification else "assistant"
    msg = add_message(
        session_id=session_id,
        role=role,
        content=answer,
        db=db,
        confidence_score=overall_conf,
        citations=citations
    )
    
    # 4. Update session title if it's the first query
    if is_new_session:
        # Simple title generation: first 40 chars of user query
        title = (query[:37] + "...") if len(query) > 40 else query
        update_session_title(session_id, title, db)
    
    # 5. Log Knowledge Gaps — use SHORT root phrases so all Gemini variations are caught.
    #    e.g. "no information given about" was missed by "no information about"
    #    By matching shorter roots we catch all variants.
    NO_ANSWER_PHRASES = [
        "no information",          # catches: "no information given about", "no information on", etc.
        "no mention",              # catches: "no mention of", "there is no mention"
        "not mentioned",           # catches: "not mentioned in the document"
        "not discussed",           # catches: "not discussed in the provided"
        "not found",               # catches: "not found in the document"
        "not covered",             # catches: "not covered in"
        "not in the document",
        "cannot find",
        "no relevant information",
        "not provided",
        "does not mention",
        "not available",
        "i don't have enough",
        "does not contain",
        "not contain information",
        "only contains information",  # catches: "only contains info about NPS, not pav bhaji"
        "only discusses",
        "only covers",
        "unrelated to",
        "outside the scope",
        "not related to",
    ]
    lower_answer = answer.lower()
    is_unanswered = any(phrase in lower_answer for phrase in NO_ANSWER_PHRASES)

    # Also flag when retrieval completely failed (0 retrieval confidence = nothing matched)
    zero_retrieval = r_conf == 0.0 and not is_clarification
    is_low_confidence = (overall_conf < KNOWLEDGE_GAP_THRESHOLD and not is_clarification)
    
    if is_unanswered or is_low_confidence or zero_retrieval:
        try:
            gap_log = KnowledgeGapLog(
                query_text=query,
                query_type=query_type,
                confidence_score=overall_conf,
                was_answered=not is_unanswered,
            )
            db.add(gap_log)
            db.commit()
        except Exception as e:
            # Don't let logging errors break the main flow
            print(f"Warning: Failed to log knowledge gap: {e}")
            db.rollback()
        
    # Return updated state with session_id and message_id
    return {
        "session_id": session_id,
        "message_id": msg.id
    }
