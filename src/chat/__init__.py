"""
Virtual Pamudu Chat Package

A modular chat agent with multi-turn conversation support.
This package provides all components for the chat system.
"""

# Re-export schemas
from .schemas import (
    AgentState,
    SearchParams,
    EmailParams,
    ToolCall,
    AgentPlan,
    Citation,
    AgentResponse,
    SHORTCUT_KEYS,
    ShortcutKey,
)

# Re-export LLM
from .llm import get_llm

# Re-export nodes
from .nodes import planner_node, executor_node, synthesizer_node

# Re-export graph
from .graph import app, should_search

# Re-export session
from .session import ChatSession

# Re-export CLI
from .cli import start_chat

__all__ = [
    # Schemas
    "AgentState",
    "SearchParams", 
    "EmailParams",
    "ToolCall",
    "AgentPlan",
    "Citation",
    "AgentResponse",
    "SHORTCUT_KEYS",
    "ShortcutKey",
    # LLM
    "get_llm",
    # Nodes
    "planner_node",
    "executor_node", 
    "synthesizer_node",
    # Graph
    "app",
    "should_search",
    # Session
    "ChatSession",
    # CLI
    "start_chat",
]
