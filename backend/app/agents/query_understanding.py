import json
import httpx
from typing import Dict, Any, List
from app.core.config import settings

def query_understanding_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query Understanding Agent LangGraph Node.
    
    Input state keys expected:
      - query (str): The raw user query.
      - chat_history (list): List of previous messages (dict with 'role' and 'content').
      
    Output state updates:
      - query_type (str): factual, procedural, comparative, or ambiguous.
      - normalized_query (str): The query with resolved pronouns based on context.
      - query_confidence (float): Confidence score (0.0 to 1.0).
    """
    query = state.get("query", "")
    chat_history = state.get("chat_history", [])
    
    # Format chat history for the prompt
    history_text = "None"
    if chat_history:
        history_lines = [f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in chat_history]
        history_text = "\n".join(history_lines)

    system_prompt = (
        "You are the Query Understanding Agent for a Knowledge Base system. "
        "Analyze the user's query and the chat history.\n\n"
        "1. Classify the query into exactly one of these types:\n"
        "   - factual: Asking for specific facts or information.\n"
        "   - procedural: Asking for instructions or how to do something.\n"
        "   - comparative: Asking to compare multiple items, policies, etc.\n"
        "   - ambiguous: The query is too vague, unclear, or lacks enough context to be answered.\n\n"
        "2. Generate a 'normalized_query'. Resolve any pronouns (it, they, he) or vague references "
        "using the chat history so the query can be understood completely on its own.\n\n"
        "3. Provide a 'confidence' score between 0.0 and 1.0 representing how confident you are in your classification.\n\n"
        "Respond ONLY with a JSON object containing EXACTLY these keys: "
        '"query_type" (string), "normalized_query" (string), and "confidence" (float).'
    )

    prompt = f"Chat History:\n{history_text}\n\nUser Query: {query}"

    payload = {
        "model": settings.OLLAMA_CHAT_MODEL,
        "system": system_prompt,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.0  # low temp for consistent classification
        }
    }
    
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    
    try:
        resp = httpx.post(url, json=payload, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        response_text = data.get("response", "{}")
        
        parsed = json.loads(response_text)
        
        return {
            "query_type": parsed.get("query_type", "ambiguous").lower(),
            "normalized_query": parsed.get("normalized_query", query),
            "query_confidence": float(parsed.get("confidence", 0.0))
        }
        
    except (httpx.HTTPError, json.JSONDecodeError, ValueError) as e:
        # Fallback if LLM fails or returns invalid JSON
        return {
            "query_type": "ambiguous",
            "normalized_query": query,
            "query_confidence": 0.0
        }
