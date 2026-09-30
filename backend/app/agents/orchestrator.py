from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

from app.agents.query_understanding import query_understanding_node
from app.agents.retrieval import retrieval_node
from app.agents.response_generation import response_generation_node
from app.agents.clarification import clarification_node
from app.agents.memory import memory_node

class AgentState(TypedDict):
    # Inputs & Context
    query: str
    chat_history: List[Dict[str, str]]
    session_id: Optional[int]
    user_id: Optional[int]
    db: Optional[Any]  # SQLAlchemy Session
    message_id: Optional[int]
    
    # Query Understanding Outputs
    query_type: Optional[str]
    normalized_query: Optional[str]
    query_confidence: Optional[float]
    
    # Clarification Outputs
    clarification_needed: Optional[bool]
    clarifying_question: Optional[str]
    
    # Retrieval Outputs
    chunks: Optional[List[Dict[str, Any]]]
    retrieval_confidence: Optional[float]
    
    # Response Generation Outputs
    answer_text: Optional[str]
    citations: Optional[List[Dict[str, str]]]
    generation_confidence: Optional[float]

# 1. Initialize StateGraph
graph = StateGraph(AgentState)

# 2. Add Nodes
graph.add_node("query_understanding", query_understanding_node)
graph.add_node("clarification", clarification_node)
graph.add_node("retrieval", retrieval_node)
graph.add_node("response_generation", response_generation_node)
graph.add_node("memory", memory_node)

# 3. Define Conditional Routing Function
def route_after_understanding(state: AgentState):
    """Route to clarification if ambiguous, else proceed to retrieval."""
    if state.get("query_type") == "ambiguous":
        return "clarification"
    return "retrieval"

# 4. Add Edges
graph.add_edge(START, "query_understanding")

# Conditional branch after query understanding
graph.add_conditional_edges(
    "query_understanding",
    route_after_understanding,
    {
        "clarification": "clarification",
        "retrieval": "retrieval"
    }
)

# Clarification goes straight to memory (to save the question), then ends
graph.add_edge("clarification", "memory")

# Normal flow goes to response generation, then memory, then ends
graph.add_edge("retrieval", "response_generation")
graph.add_edge("response_generation", "memory")
graph.add_edge("memory", END)

# 5. Compile Graph
orchestrator = graph.compile()
