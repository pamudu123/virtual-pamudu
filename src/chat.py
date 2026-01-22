"""
Virtual Pamudu Chat - Backwards Compatibility Module

This module re-exports everything from the chat package for backwards compatibility.
All functionality has been refactored into the chat/ package.

Structure:
    chat/
    ├── __init__.py      - Public exports
    ├── schemas.py       - Pydantic models (AgentState, AgentPlan, etc.)
    ├── llm.py           - LLM configuration (get_llm)
    ├── nodes/           - Graph nodes
    │   ├── planner.py   - Planning node
    │   ├── executor.py  - Tool execution node
    │   └── synthesizer.py - Response generation node
    ├── graph.py         - LangGraph workflow (app)
    ├── session.py       - ChatSession class
    └── cli.py           - Interactive CLI (start_chat)
"""

# Re-export everything from the chat package
from chat import (
    # Schemas
    AgentState,
    SearchParams,
    EmailParams,
    ToolCall,
    AgentPlan,
    Citation,
    AgentResponse,
    SHORTCUT_KEYS,
    ShortcutKey,
    # LLM
    get_llm,
    # Nodes
    planner_node,
    executor_node,
    synthesizer_node,
    # Graph
    app,
    should_search,
    # Session
    ChatSession,
    # CLI
    start_chat,
)

__all__ = [
    "AgentState",
    "SearchParams",
    "EmailParams",
    "ToolCall",
    "AgentPlan",
    "Citation",
    "AgentResponse",
    "SHORTCUT_KEYS",
    "ShortcutKey",
    "get_llm",
    "planner_node",
    "executor_node",
    "synthesizer_node",
    "app",
    "should_search",
    "ChatSession",
    "start_chat",
]


if __name__ == "__main__":
    start_chat()
