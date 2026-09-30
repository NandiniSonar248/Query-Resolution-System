import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.orchestrator import orchestrator

def run_tests():
    print("Testing LangGraph Orchestrator (End-to-End)...\n")
    print("NOTE: This requires Ollama and ChromaDB to be running.\n")

    initial_state = {
        "query": "What is the maximum file size for document uploads?",
        "chat_history": []
    }

    print("--- Input State ---")
    print("Query:", initial_state["query"])
    print("Executing Graph...\n")

    try:
        final_state = orchestrator.invoke(initial_state)

        print("--- Final Output State ---")
        print(f"Query Type: {final_state.get('query_type')}")
        print(f"Normalized Query: {final_state.get('normalized_query')}")
        
        print(f"\nRetrieval Confidence: {final_state.get('retrieval_confidence')}")
        chunks = final_state.get("chunks", [])
        print(f"Chunks Retrieved: {len(chunks)}")
        
        print(f"\nGeneration Confidence: {final_state.get('generation_confidence')}")
        print(f"Answer: {final_state.get('answer_text')}")
        
        citations = final_state.get("citations", [])
        print(f"Citations ({len(citations)}):")
        for c in citations:
            print(f"  - {c.get('source_doc')} (Chunk {c.get('chunk_id')})")
            
    except Exception as e:
        print(f"Orchestrator failed: {e}")

if __name__ == "__main__":
    run_tests()
