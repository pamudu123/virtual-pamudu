"""Presentation tools.

These tools do almost no work on the server. The chat frontend renders their
arguments and results as rich components (cards, timelines, chips), so calling
one is how the agent puts UI into the conversation.
"""

from pathlib import Path
from typing import Literal

import yaml
from langchain_core.tools import tool
from langgraph.types import interrupt
from pydantic import BaseModel, Field

BRAIN_DIR = Path(__file__).resolve().parents[2] / "digital_brain"


class ProfileItem(BaseModel):
    """One entry in a profile section."""

    title: str = Field(description="Main line, e.g. a job title, degree, project or paper name.")
    subtitle: str = Field(default="", description="Secondary line, e.g. organisation or venue.")
    period: str = Field(default="", description="Dates, e.g. 'Jul 2024 - Aug 2025'.")
    description: str = Field(default="", description="One or two short sentences.")
    tags: list[str] = Field(default_factory=list, description="Short labels, e.g. skills or technologies.")
    url: str = Field(default="", description="Link, if the source file has one.")


@tool
def show_profile_section(
    section: Literal["experience", "education", "projects", "skills", "awards", "publications"],
    heading: str,
    items: list[ProfileItem],
) -> str:
    """Show part of Pamudu's profile as a visual component in the chat.

    Use this instead of long bullet lists when the visitor asks about
    experience, education, projects, skills, awards or publications. Fill the
    items only with facts you have read from the knowledge base. For skills,
    use one item per skill group with the skills in `tags`.

    Args:
        section: Which kind of section this is; it selects the layout.
        heading: Short heading shown above the component.
        items: The entries to show, most relevant or most recent first.
    """
    return f"Displayed {len(items)} {section} item(s) to the visitor. Do not repeat them as a list."


@tool
def show_contact_card() -> dict:
    """Show Pamudu's public contact links (LinkedIn, GitHub, YouTube, Scholar) as a card."""
    profile = yaml.safe_load((BRAIN_DIR / "profile" / "profile.yaml").read_text(encoding="utf-8"))
    return {
        "name": profile.get("name", "Pamudu Ranasinghe"),
        "roles": profile.get("current_roles", []),
        "location": (profile.get("location") or {}).get("primary", ""),
        "links": profile.get("links", {}),
    }


@tool
def ask_visitor(question: str, options: list[str] | None = None) -> str:
    """Ask the visitor a clarifying question and wait for their answer.

    Use this when a request is ambiguous or you need to know what the visitor
    cares about before you can give a useful answer (for example which project,
    or whether they are hiring, collaborating or just curious). Ask one question
    at a time and only when it changes what you would show.

    Args:
        question: The question, one short sentence.
        options: 2 to 4 short answer choices shown as buttons. The visitor can
            also type their own answer. Leave empty for an open question.
    """
    answer = interrupt(
        {"type": "ask_visitor", "question": question, "options": list(options or [])[:4]}
    )
    if isinstance(answer, dict):
        answer = answer.get("answer", "")
    return f"The visitor answered: {answer}" if answer else "The visitor skipped the question."


@tool(return_direct=True)
def suggest_followups(questions: list[str]) -> str:
    """Offer the visitor follow-up questions as clickable chips. This ends your turn.

    Call this in the same message as your final answer, every turn.

    Args:
        questions: Exactly 3 short questions (under 10 words each) the visitor
            might ask next, written from the visitor's point of view.
    """
    return "Follow-up suggestions shown."
