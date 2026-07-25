import sys
import os

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.response_generation import response_generation_node

def run_tests():
    print("Testing Response Generation Agent Node...\n")
    print("NOTE: This test requires Ollama to be running with the configured model.\n")

    # Mock state coming from Retrieval Agent
    state_success = {
        "normalized_query": "What is the maximum upload size for documents?",
        "chat_history": [],
        "chunks": [
            {
                "chunk_id": "doc1_chunk1",
                "source_doc": "employee_handbook.pdf",
                "text": "The platform allows users to upload various document types. The maximum upload size for any single document is 50MB."
            },
            {
                "chunk_id": "doc2_chunk4",
                "source_doc": "system_limits.txt",
                "text": "For performance reasons, we cap uploads. Please ensure files do not exceed the 50MB limit."
            }
        ]
    }

    print("--- Test 1: Sufficient Context ---")
    print(f"Query: '{state_success['normalized_query']}'")
    try:
        result1 = response_generation_node(state_success)
        print("Answer Text:", result1.get("answer_text"))
        print("Citations:", result1.get("citations"))
        print("Confidence:", result1.get("generation_confidence"))
    except Exception as e:
        print(f"Error: {e}")
    print("\n")


    # Mock state with insufficient context
    state_fail = {
        "normalized_query": "What is the CEO's favorite color?",
        "chat_history": [],
        "chunks": [
            {
                "chunk_id": "doc1_chunk1",
                "source_doc": "employee_handbook.pdf",
                "text": "The CEO of the company is John Doe. He started the company in 2010."
            }
        ]
    }

    print("--- Test 2: Insufficient Context (Should fail gracefully) ---")
    print(f"Query: '{state_fail['normalized_query']}'")
    try:
        result2 = response_generation_node(state_fail)
        print("Answer Text:", result2.get("answer_text"))
        print("Citations:", result2.get("citations"))
        print("Confidence:", result2.get("generation_confidence"))
    except Exception as e:
        print(f"Error: {e}")
    print("\n")

if __name__ == "__main__":
    run_tests()
