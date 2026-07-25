import json
import httpx
from typing import Dict, Any, List
from app.core.config import settings

def response_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Response Generation Agent LangGraph Node.
    
    Input state keys expected:
      - normalized_query (str): The context-resolved query.
      - chunks (list): Retrieved chunks from the Retrieval Agent.
      - chat_history (list): List of previous messages.
      
    Output state updates:
      - answer_text (str): The generated answer.
      - citations (list): List of citations [{'chunk_id': '...', 'source_doc': '...'}]
      - generation_confidence (float): Confidence score (0.0 to 1.0)
    """
    normalized_query = state.get("normalized_query", "")
    chunks = state.get("chunks", [])
    chat_history = state.get("chat_history", [])
    
    # 1. Handle case where no chunks were found
    if not chunks:
        return {
            "answer_text": "I don't have enough information.",
            "citations": [],
            "generation_confidence": 0.0
        }
        
    # 2. Format chunks for the prompt
    chunks_text = ""
    for c in chunks:
        chunk_id = c.get("chunk_id", "unknown_chunk")
        source = c.get("source_doc", "unknown_source")
        text = c.get("text", "")
        chunks_text += f"--- Chunk ID: {chunk_id} | Source: {source} ---\n{text}\n\n"
        
    # 3. Format chat history
    history_text = "None"
    if chat_history:
        history_lines = [f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in chat_history]
        history_text = "\n".join(history_lines)
        
    # 4. Construct System Prompt
    system_prompt = (
        "You are an expert answering questions based strictly on the provided Context Chunks. "
        "Do not use any outside knowledge.\n\n"
        "Instructions:\n"
        "1. Read the Context Chunks to find the answer to the User Query.\n"
        "2. If the context does not contain the answer, your answer_text MUST be exactly: \"I don't have enough information.\"\n"
        "3. If you find the answer, write a clear response in answer_text. Do not include inline citation numbers in the text.\n"
        "4. Provide a list of 'citations'. Each citation is an object with 'chunk_id' and 'source_doc' corresponding to the chunks you used. "
        "If you could not answer, citations should be an empty list.\n"
        "5. Provide a 'generation_confidence' float score between 0.0 and 1.0 indicating how well the context supports your answer. "
        "If you could not answer, set confidence to 0.0.\n\n"
        "Respond ONLY with a JSON object containing EXACTLY these keys: "
        '"answer_text" (string), "citations" (list of objects with "chunk_id" and "source_doc"), and "generation_confidence" (float).'
    )
    
    prompt = f"Context Chunks:\n{chunks_text}\nChat History:\n{history_text}\n\nUser Query: {normalized_query}"
    
    payload = {
        "model": settings.OLLAMA_CHAT_MODEL,
        "system": system_prompt,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.1  # low temp for grounded facts
        }
    }
    
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    
    try:
        resp = httpx.post(url, json=payload, timeout=60.0)
        resp.raise_for_status()
        data = resp.json()
        response_text = data.get("response", "{}")
        
        parsed = json.loads(response_text)
        
        return {
            "answer_text": parsed.get("answer_text", "I don't have enough information."),
            "citations": parsed.get("citations", []),
            "generation_confidence": float(parsed.get("generation_confidence", 0.0))
        }
        
    except (httpx.HTTPError, json.JSONDecodeError, ValueError) as e:
        # Fallback if LLM fails
        return {
            "answer_text": "I encountered an error generating the response.",
            "citations": [],
            "generation_confidence": 0.0
        }
