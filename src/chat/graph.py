"""
LangGraph workflow building and compilation.
"""

import structlog
from langgraph.graph import StateGraph, END

from .schemas import AgentState
from .nodes import planner_node, executor_node, synthesizer_node

logger = structlog.get_logger()


# --- CONDITIONAL EDGE ---

def should_search(state: AgentState) -> str:
    """
    Decides whether to go to Executor or straight to Synthesizer.
    Returns 'search' if plan has queries, 'skip' otherwise.
    """
    if not state.get('plan'):
        logger.info("skip_search")
        return "skip"
    return "search"


# --- BUILD THE GRAPH ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)
workflow.add_node("synthesizer", synthesizer_node)

# Set Entry Point
workflow.set_entry_point("planner")

# Add Edges
workflow.add_conditional_edges(
    "planner",
    should_search,
    {
        "search": "executor",
        "skip": "synthesizer"
    }
)

workflow.add_edge("executor", "synthesizer")
workflow.add_edge("synthesizer", END)

# Compile the graph
app = workflow.compile()
