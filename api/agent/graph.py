"""Builds the Virtual Pamudu deep agent."""

import os
from pathlib import Path

from copilotkit import CopilotKitMiddleware
from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, StateBackend
from deepagents.middleware import FilesystemMiddleware
from langchain.agents.middleware import TodoListMiddleware
from langchain_openrouter import ChatOpenRouter
from langgraph.checkpoint.base import BaseCheckpointSaver

from . import tools as t
from .prompts import CODE_RESEARCHER_PROMPT, CONTENT_RESEARCHER_PROMPT, SYSTEM_PROMPT

BRAIN_DIR = Path(__file__).resolve().parents[1] / "digital_brain"
DEFAULT_MODEL = "google/gemini-3-flash-preview"
READ_ONLY_FS_TOOLS = ["ls", "read_file", "glob", "grep"]


def build_model() -> ChatOpenRouter:
    """The chat model, served through OpenRouter."""
    return ChatOpenRouter(model=os.getenv("AGENT_MODEL", DEFAULT_MODEL), temperature=0)


def build_backend() -> CompositeBackend:
    """Knowledge base on disk under /brain/, everything else in per-thread state.

    Large tool results that deepagents offloads go to the state backend, so
    nothing is ever written to the server's disk.
    """
    return CompositeBackend(
        default=StateBackend(),
        routes={"/brain/": FilesystemBackend(root_dir=str(BRAIN_DIR), virtual_mode=True)},
    )


def build_agent(checkpointer: BaseCheckpointSaver):
    """Create the compiled deep agent graph.

    This is a public, anonymous-visitor agent, so the filesystem is read-only
    twice over: the write/edit/delete/execute tools are not exposed at all, and
    a deny rule blocks writes if they ever were.
    """
    model = build_model()
    backend = build_backend()

    return create_deep_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            t.list_github_repos,
            t.search_github_repos,
            t.list_medium_articles,
            t.search_medium_articles,
            t.list_youtube_videos,
            t.search_youtube_videos,
            t.show_profile_section,
            t.show_contact_card,
            t.show_stats,
            t.show_role_fit,
            t.show_quick_actions,
            t.ask_visitor,
            t.send_message_to_pamudu,
            t.suggest_followups,
        ],
        subagents=[
            {
                "name": "code-researcher",
                "description": (
                    "Reads Pamudu's GitHub repositories (READMEs and source files) and returns a "
                    "summary. Use for questions about how a project works or what it contains."
                ),
                "system_prompt": CODE_RESEARCHER_PROMPT,
                "tools": [t.search_github_repos, t.list_github_repos, t.get_repo_readme, t.get_repo_file],
            },
            {
                "name": "content-researcher",
                "description": (
                    "Reads the full text of Pamudu's Medium articles and YouTube transcripts and "
                    "returns a summary. Use for questions about what an article or video says."
                ),
                "system_prompt": CONTENT_RESEARCHER_PROMPT,
                "tools": [
                    t.search_medium_articles,
                    t.list_medium_articles,
                    t.read_medium_article,
                    t.search_youtube_videos,
                    t.list_youtube_videos,
                    t.get_video_transcript,
                ],
            },
        ],
        backend=backend,
        memory=["/brain/AGENTS.md"],
        # Task playbooks, one folder per skill, read on demand.
        skills=["/brain/skills/"],
        permissions=[FilesystemPermission(operations=["write"], paths=["/**"], mode="deny")],
        middleware=[
            FilesystemMiddleware(backend=backend, tools=READ_ONLY_FS_TOOLS),
            TodoListMiddleware(),
            CopilotKitMiddleware(),
        ],
        interrupt_on={
            "send_message_to_pamudu": {"allowed_decisions": ["approve", "edit", "reject"]},
        },
        checkpointer=checkpointer,
        name="virtual_pamudu",
    )
