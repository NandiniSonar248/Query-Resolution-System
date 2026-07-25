import sys
import os

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.retrieval import retrieval_node

def run_tests():
    print("Testing Retrieval Agent Node...\n")
    print("NOTE: This test requires Ollama and ChromaDB to be running.")
    print("It will attempt to embed the query and search your local ChromaDB.\n")

    # Mock state coming from Query Understanding Agent
    state = {
        "query_type": "factual",
        "normalized_query": "What is the company policy on remote work?",
        "query_confidence": 0.95
    }

    print("--- Input State ---")
    print(f"Normalized Query: '{state['normalized_query']}'\n")

    try:
        # Call the retrieval node
        result = retrieval_node(state)
        
        print("--- Result State Updates ---")
        print(f"Retrieval Confidence: {result.get('retrieval_confidence')}")
        
        chunks = result.get("chunks", [])
        print(f"Retrieved {len(chunks)} chunks above the similarity threshold.")
        
        for i, chunk in enumerate(chunks, 1):
            print(f"\nChunk {i}:")
            print(f"  Source: {chunk.get('source_doc_name')} (ID: {chunk.get('document_id')})")
            print(f"  Similarity: {chunk.get('similarity_score'):.4f}")
            print(f"  Text Excerpt: {chunk.get('text', '')[:100]}...")
            
    except Exception as e:
        print("\n[ERROR] Retrieval failed. Ensure Ollama is running, the model is pulled,")
        print(f"and the environment is correctly set up. Details: {e}")

if __name__ == "__main__":
    run_tests()
