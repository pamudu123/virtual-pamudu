"""
Pydantic models and TypedDict definitions for the chat agent.
"""

import operator
from typing import Annotated, TypedDict, Literal, Optional, Union

from pydantic import BaseModel, Field

from utils import load_shortcut_keys

# Load shortcut keys at module level for use as type
SHORTCUT_KEYS = load_shortcut_keys()
ShortcutKey = Literal[SHORTCUT_KEYS]  # type: ignore


# --- STATE DEFINITION ---

class AgentState(TypedDict):
    """Shared memory state for the agent graph."""
    query: str
    # Conversation history for multi-turn coherence
    conversation_history: list[dict]  # [{"role": "user/assistant", "content": "..."}]
    # 'plan' is a list of search arguments (shortcuts/keywords)
    plan: list[dict]
    # 'results' is a list of strings found from the tools
    results: Annotated[list[str], operator.add]
    # Structured final response with citations
    final_answer: str
    citations: list[dict]


# --- TOOL PARAMETER MODELS ---

class SearchParams(BaseModel):
    """Parameters for search/retrieval tools (brain, medium, youtube, github)."""
    shortcuts: list[ShortcutKey] = Field(default_factory=list, description=f"Brain shortcuts: {', '.join(SHORTCUT_KEYS)}.")
    keywords: list[str] = Field(default_factory=list, description="Search keywords.")
    limit: int = Field(default=5, description="Max results to return.")
    repo_name: str = Field(default="", description="GitHub repository name.")
    file_path: str = Field(default="", description="Path to file in repo (e.g., 'src/main.py').")
    article_link: str = Field(default="", description="Medium article URL.")
    video_id: str = Field(default="", description="YouTube video ID.")
    state: str = Field(default="open", description="PR state: open, closed, all.")


class EmailParams(BaseModel):
    """Parameters for sending an email."""
    email_to: str = Field(description="Recipient email address.")
    email_subject: str = Field(description="Email subject line.")
    email_content: str = Field(description="Email body content.")
    email_cc: str = Field(default="", description="CC email address (optional).")


# --- PLAN MODELS ---

class ToolCall(BaseModel):
    """A single tool call in the plan."""
    tool: str = Field(
        description="The tool to use: 'brain', 'medium', 'youtube', 'github', or 'email'."
    )
    action: str = Field(
        description="The specific action: 'search', 'list', 'get_content', 'get_transcript', 'get_readme', 'get_file', 'search_and_read', 'send'."
    )
    params: Union[SearchParams, EmailParams] = Field(
        description="Parameters for the tool call. Use EmailParams for 'email' tool, SearchParams for others."
    )


class AgentPlan(BaseModel):
    """The plan to retrieve information."""
    need_external_info: bool = Field(
        description="True if you need to fetch data, False if you can answer directly."
    )
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="List of tool calls to execute."
    )
    response: Optional[str] = Field(
        default=None,
        description="The answer to the user if no external info is needed."
    )


# --- RESPONSE MODELS ---

class Citation(BaseModel):
    """A single citation/source reference."""
    source_type: str = Field(
        description="Type of source: 'brain', 'github', 'medium', 'youtube', 'email'"
    )
    source_name: str = Field(
        description="Name of the source (e.g., repo name, article title, file name)"
    )
    url: str = Field(
        default="",
        description="URL to the source if available"
    )


class AgentResponse(BaseModel):
    """Structured response from the agent with citations."""
    answer: str = Field(
        description="The main response text answering the user's query"
    )
    citations: list[Citation] = Field(
        default_factory=list,
        description="List of sources used to generate the answer"
    )
