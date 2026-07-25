import sys
import os

# Add the backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.query_understanding import query_understanding_node

def run_tests():
    print("Testing Query Understanding Agent...\n")

    # Test 1: Factual Query (No history)
    print("--- Test 1: Factual Query ---")
    state1 = {
        "query": "What is the maximum upload size for documents?",
        "chat_history": []
    }
    result1 = query_understanding_node(state1)
    print("Input Query:", state1["query"])
    print("Result:", result1)
    print("\n")

    # Test 2: Pronoun Resolution using Chat History (Procedural)
    print("--- Test 2: Pronoun Resolution ---")
    state2 = {
        "query": "How do I reset it?",
        "chat_history": [
            {"role": "user", "content": "I forgot my password."},
            {"role": "assistant", "content": "You can use the password reset tool."}
        ]
    }
    result2 = query_understanding_node(state2)
    print("Chat History:", state2["chat_history"])
    print("Input Query:", state2["query"])
    print("Result:", result2)
    print("\n")

    # Test 3: Ambiguous Query
    print("--- Test 3: Ambiguous Query ---")
    state3 = {
        "query": "What about the other one?",
        "chat_history": []
    }
    result3 = query_understanding_node(state3)
    print("Input Query:", state3["query"])
    print("Result:", result3)
    print("\n")

if __name__ == "__main__":
    run_tests()
