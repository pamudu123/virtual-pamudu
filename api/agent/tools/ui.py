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
    url: str = Field(
        default="",
        description=(
            "Public link that opens when the visitor clicks the card, e.g. the 'Paper URL' of a "
            "publication or a project's repository. Always fill it when the source file gives one; "
            "leave empty otherwise. Never invent a link."
        ),
    )


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


class Stat(BaseModel):
    """One headline number."""

    value: str = Field(description="The figure itself, kept short, e.g. '10M+', '250K', '70-80%', '4+ years'.")
    label: str = Field(description="What the figure measures, in a few words, e.g. 'daily interactions'.")
    note: str = Field(default="", description="Optional context, e.g. the product or employer it comes from.")


@tool
def show_stats(heading: str, stats: list[Stat]) -> str:
    """Show headline numbers about Pamudu's work as a row of stat tiles.

    Use this when numbers make the point better than sentences: an overview of
    him, the impact of a role or project, or a recruiter asking what he has
    delivered. Use only figures that appear in the knowledge base, exactly as
    written there. Never estimate, round up or invent a number.

    Args:
        heading: Short heading shown above the tiles, e.g. "Impact at a glance".
        stats: 2 to 6 tiles, strongest first.
    """
    return f"Displayed {len(stats)} stat tile(s) to the visitor. Do not repeat the numbers as a list."


class FitItem(BaseModel):
    """One requirement of a role, with what in Pamudu's background meets it."""

    requirement: str = Field(description="The requirement, in a few words, e.g. 'Production LLM systems'.")
    evidence: str = Field(
        default="",
        description="One short sentence naming the role, project or paper that shows it. Facts from the knowledge base only.",
    )


@tool
def show_role_fit(
    role: str,
    strong: list[FitItem],
    partial: list[FitItem],
    gaps: list[str],
    summary: str,
) -> str:
    """Show how Pamudu's background matches a role, as a role fit card.

    Use this when a visitor shares a job description or names a role and asks
    whether he is a fit. Read his experience, skills and projects first. Be
    honest: put a requirement under `strong` only when the knowledge base
    clearly shows it, under `partial` when he has related but not identical
    experience, and under `gaps` when nothing in the knowledge base covers it.

    Args:
        role: The role's title, e.g. "Senior ML Engineer at Acme".
        strong: Requirements he clearly meets, each with its evidence.
        partial: Requirements he partly meets, each with what he does have.
        gaps: Requirements the knowledge base does not cover, a few words each.
        summary: One or two sentences giving the overall picture.
    """
    return (
        f"Displayed a role fit card for '{role}' ({len(strong)} strong, {len(partial)} partial, "
        f"{len(gaps)} not covered). Do not repeat it as a list."
    )


# Quick actions are a fixed menu: links come from the profile file and prompts
# are written here, so the model can never put an invented URL on a button.
QUICK_ACTION_LINKS = {
    "linkedin": "View LinkedIn",
    "github": "View GitHub",
    "youtube": "Watch on YouTube",
    "google_scholar": "View Google Scholar",
}
QUICK_ACTION_PROMPTS = {
    "message": ("Send him a message", "I'd like to send Pamudu a message."),
    "role_fit": ("Check fit for a role", "I have a role in mind. Can you check how well Pamudu fits it?"),
    "experience": ("See his experience", "Walk me through Pamudu's work experience."),
    "projects": ("See his projects", "Show me Pamudu's best projects."),
    "skills": ("See his skills", "What are Pamudu's main skills?"),
    "research": ("See his research", "What research has Pamudu published?"),
}
QuickAction = Literal[
    "message", "role_fit", "experience", "projects", "skills", "research",
    "linkedin", "github", "youtube", "google_scholar",
]


@tool
def show_quick_actions(actions: list[QuickAction]) -> dict:
    """Show a row of quick action buttons under your answer.

    Use this when there is an obvious next step for the visitor: after a role
    fit card, when they show hiring or collaboration interest, or after an
    overview of him. Link buttons open his public profiles; the others start
    that conversation for the visitor. Use it at most once per answer and not
    on every turn.

    Args:
        actions: 2 to 4 actions, most useful first.
    """
    profile = yaml.safe_load((BRAIN_DIR / "profile" / "profile.yaml").read_text(encoding="utf-8"))
    links = profile.get("links") or {}
    resolved = []
    for action in dict.fromkeys(actions):
        if action in QUICK_ACTION_PROMPTS:
            label, prompt = QUICK_ACTION_PROMPTS[action]
            resolved.append({"id": action, "kind": "prompt", "label": label, "prompt": prompt})
        elif action in QUICK_ACTION_LINKS and links.get(action):
            resolved.append(
                {"id": action, "kind": "link", "label": QUICK_ACTION_LINKS[action], "href": links[action]}
            )
    return {"actions": resolved[:4]}


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
def ask_visitor(
    question: str,
    options: list[str] | None = None,
    fields: list[str] | None = None,
) -> str:
    """Show the visitor a question panel in the chat and wait for their answer.

    Two ways to use it:

    - A choice: pass `options`. Use this when a request is ambiguous or you
      need to know what the visitor cares about before you can give a useful
      answer (for example which project, or whether they are hiring,
      collaborating or just curious).
    - A small form: pass `fields`. Use this when you need short details from
      the visitor, such as their name and email before sending Pamudu a
      message. All fields are answered together in one panel.

    Ask one panel at a time and only when it changes what you would do. Never
    ask for these things in plain text instead.

    Args:
        question: The question or prompt, one short sentence.
        options: 2 to 4 short answer choices shown as buttons. The visitor can
            also type their own answer. Leave empty when using `fields`.
        fields: 1 to 4 short labels, one text input each, e.g.
            ["Your name", "Your email"]. A label containing "email" is checked
            as an email address. Leave empty when using `options`.
    """
    answer = interrupt(
        {
            "type": "ask_visitor",
            "question": question,
            "options": list(options or [])[:4],
            "fields": [str(f) for f in (fields or [])][:4],
        }
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
