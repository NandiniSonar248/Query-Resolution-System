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
    
    # 1. Handle case where no chunks were found
    if not chunks:
        return {
            "answer_text": "I don't have enough information in the knowledge base to answer this question. Please upload relevant documents first.",
            "citations": [],
            "generation_confidence": 0.0
        }
        
    # 2. Format chunks for the prompt (Gemini has a 1M token context, so we can pass all retrieved chunks)
    chunks_text = ""
    citation_list = []
    for c in chunks:
        chunk_id = c.get("chunk_id", "unknown_chunk")
        source = c.get("source_doc", "unknown_source")
        citation_list.append({"chunk_id": chunk_id, "source_doc": source})
        
        text = c.get("text", "")
        chunks_text += f"{text}\n\n"

    # 3. Assertive prompt optimized for small models (llama3.2:1b)
    system_prompt = (
        "You are a document summary assistant. "
        "You will be given text extracted from company documents. "
        "Your job is to summarize the relevant information clearly and accurately. "
        "Only use the text provided. Do not add any outside information."
    )
    
    prompt = f"Here is text from the company documents:\n\n{chunks_text}\nSummarize what the documents say about: {normalized_query}"
    
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_CHAT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2
            )
        )
        answer = response.text.strip()
        
        if not answer:
            answer = "I couldn't generate an answer. Please try rephrasing your question."
        
        # Calculate confidence dynamically from retrieval scores
        avg_similarity = sum(c.get("similarity_score", 0.5) for c in chunks) / len(chunks)
        
        # We use the same broad phrases we use in memory.py to detect an unanswered query
        NO_ANSWER_PHRASES = [
            "no information", "no mention", "not mentioned", "not discussed",
            "not found", "not covered", "not in the document", "cannot find",
            "no relevant information", "not provided", "does not mention",
            "not available", "i don't have enough", "i cannot", "does not contain",
            "not contain information", "only contains information", "only discusses",
            "only covers", "unrelated to", "outside the scope", "not related to"
        ]
        
        is_unanswered = any(phrase in answer.lower() for phrase in NO_ANSWER_PHRASES)
        
        if is_unanswered:
            confidence = max(0.0, avg_similarity * 0.1) # Extremely low confidence
            citation_list = [] # Don't cite sources if we didn't find the answer in them!
        else:
            confidence = min(0.95, avg_similarity * 1.05)
        
        return {
            "answer_text": answer,
            "citations": citation_list,
            "generation_confidence": round(confidence, 4)
        }
        
    except Exception as e:
        print(f"Response Generation Error: {e}")
        # Fallback if LLM fails
        return {
            "answer_text": "I encountered an error generating the response. Please try again.",
            "citations": [],
            "generation_confidence": 0.0
        }
