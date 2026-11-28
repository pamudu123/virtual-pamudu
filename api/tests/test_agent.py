"""Structural checks on the compiled agent. No model calls are made."""

import os

import pytest
from langgraph.checkpoint.memory import MemorySaver

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

from agent.graph import BRAIN_DIR, build_agent, build_backend  # noqa: E402

FORBIDDEN_TOOLS = {"write_file", "edit_file", "delete", "execute", "eval"}
EXPECTED_TOOLS = {
    "ls",
    "read_file",
    "glob",
    "grep",
    "task",
    "write_todos",
    "list_github_repos",
    "search_github_repos",
    "list_medium_articles",
    "search_medium_articles",
    "list_youtube_videos",
    "search_youtube_videos",
    "show_profile_section",
    "show_contact_card",
    "ask_visitor",
    "send_message_to_pamudu",
    "suggest_followups",
}


@pytest.fixture(scope="module")
def graph():
    return build_agent(MemorySaver())


def _tool_names(graph) -> set[str]:
    return set(graph.nodes["tools"].bound.tools_by_name)


def test_agent_exposes_expected_tools(graph):
    assert EXPECTED_TOOLS <= _tool_names(graph)


def test_agent_cannot_write_or_execute(graph):
    assert not (FORBIDDEN_TOOLS & _tool_names(graph))


def test_knowledge_base_is_mounted_read_only_under_brain():
    backend = build_backend()
    index = backend.read("/brain/AGENTS.md")
    assert "Knowledge base index" in str(index)
    assert (BRAIN_DIR / "resume" / "experience.md").exists()


def test_brain_mount_blocks_path_traversal():
    backend = build_backend()
    with pytest.raises(ValueError, match="traversal"):
        backend.read("/brain/../main.py")


def test_send_message_skill_is_in_the_knowledge_base():
    backend = build_backend()
    skill = str(backend.read("/brain/skills/send-message/SKILL.md"))
    assert "name: send-message" in skill
    assert "Never ask for a subject" in skill
