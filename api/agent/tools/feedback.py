"""Feedback tool: a rating panel in the chat, delivered to Pamudu.

The panel is drawn by the chat frontend. This tool pauses the run until the
visitor submits or dismisses it, then passes what they entered on to Pamudu.
"""

import html
import json
import logging

from langchain_core.tools import tool
from langgraph.types import interrupt

from .mailer import deliver_to_pamudu, wrap_html

logger = logging.getLogger(__name__)

FEEDBACK_QUESTION = "Is this the best AI assistant you've seen?"
MAX_NAME_CHARS = 80
MAX_COMMENT_CHARS = 2000


def _read_answer(answer) -> dict:
    """The panel answers with an object; some transports hand it over as JSON text."""
    if isinstance(answer, str):
        try:
            answer = json.loads(answer)
        except ValueError:
            return {}
    return answer if isinstance(answer, dict) else {}


def _rating(value) -> int | None:
    try:
        rating = int(value)
    except (TypeError, ValueError):
        return None
    return rating if 1 <= rating <= 10 else None


@tool
def ask_feedback() -> str:
    """Show the feedback panel: a 1 to 10 rating, an optional name and an optional comment.

    Call this when the visitor says they want to give feedback, or picks the
    "Give feedback on this assistant" follow-up. Do not write any text before
    calling it, and never call it unprompted. The panel asks its own question,
    so do not ask for a rating, a name or a comment in text.
    """
    answer = _read_answer(interrupt({"type": "feedback", "question": FEEDBACK_QUESTION}))
    rating = _rating(answer.get("rating"))
    if rating is None:
        return "The visitor closed the feedback panel without submitting. Carry on normally and do not ask again."

    name = str(answer.get("name") or "").strip()[:MAX_NAME_CHARS]
    comment = str(answer.get("comment") or "").strip()[:MAX_COMMENT_CHARS]
    body = wrap_html(
        f"<p><strong>Question:</strong> {html.escape(FEEDBACK_QUESTION)}</p>"
        f'<p style="font-size:28px;margin:8px 0"><strong>{rating}</strong> / 10</p>'
        f"<p><strong>Name:</strong> {html.escape(name) if name else 'Not given'}</p>"
        "<p><strong>Comment:</strong><br>"
        f"{html.escape(comment).replace(chr(10), '<br>') if comment else 'None'}</p>"
    )
    error = deliver_to_pamudu(f"Feedback: {rating}/10", body)
    if error:
        # The visitor did their part; a delivery problem is ours to see in the log.
        logger.error("Feedback (%s/10) was submitted but not delivered: %s", rating, error)

    return (
        f"Feedback received ({rating}/10). Thank the visitor for their feedback in one short, warm "
        "sentence. Do not repeat their rating or comment back, do not ask for more feedback, and "
        "do not volunteer how the feedback is delivered."
    )
