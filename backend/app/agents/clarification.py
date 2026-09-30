import json
import httpx
from typing import Dict, Any
from app.core.config import settings

def clarification_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clarification Agent LangGraph Node.
    
    Triggered when query_understanding determines the query is "ambiguous".
    Uses the LLM to ask a targeted follow-up question.
    """
    query = state.get("query", "")
    chat_history = state.get("chat_history", [])
    
    # Format chat history
    history_text = "None"
    if chat_history:
        history_lines = [f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in chat_history]
        history_text = "\n".join(history_lines)

    system_prompt = (
        "You are a Clarification Agent for a Knowledge Base system. "
        "The user asked an ambiguous or unclear question. "
        "Based on the chat history and the current query, generate ONE specific, targeted "
        "follow-up question to help clarify what the user is asking. "
        "Do NOT try to answer the question. Do NOT ask generic questions like 'can you elaborate'. "
        "Ask about the specific missing context (e.g. 'Which policy are you referring to?')."
    )
    
    prompt = f"Chat History:\n{history_text}\n\nUnclear User Query: {query}\n\nClarifying Question:"
    
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_CHAT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.4
            )
        )
        question = response.text.strip()
        
        if not question:
            question = "Could you please provide more details about what you are looking for?"
            
        return {
            "clarification_needed": True,
            "clarifying_question": question,
            "answer_text": None,  # No final answer yet
            "generation_confidence": 0.0,
            "retrieval_confidence": 0.0,
            "citations": []
        }
        
    except Exception as e:
        print(f"Clarification Error: {e}")
        return {
            "clarification_needed": True,
            "clarifying_question": "Could you please provide more details? I didn't quite understand.",
            "answer_text": None,
            "generation_confidence": 0.0,
            "retrieval_confidence": 0.0,
            "citations": []
        }
