"""Contact tool: deliver a visitor's message to Pamudu by email (Brevo).

The recipient is fixed. Visitors can never choose where the email goes, and the
agent graph pauses for the visitor's explicit approval before this tool runs.
"""

import html
import logging
import os
import re

import httpx
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

BREVO_URL = "https://api.brevo.com/v3/smtp/email"
SENDER_NAME = "Virtual Pamudu"
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@tool
def send_message_to_pamudu(sender_name: str, sender_email: str, subject: str, message: str) -> dict:
    """Send a visitor's message to Pamudu's inbox.

    Call this as soon as you have the visitor's name and email address. Write
    the subject and the message yourself from what the visitor has said; never
    ask them for a subject or for the wording. The chat shows your draft as an
    editable card and nothing is sent until the visitor presses Send, so do not
    ask "shall I send it?" yourself.

    The result has `sent: true` when the email was delivered. If it has an
    `error`, nothing was sent: tell the visitor so.

    Args:
        sender_name: The visitor's name.
        sender_email: The visitor's email address, used as reply-to.
        subject: Short subject line that you write, e.g. "Hiring enquiry".
        message: Plain-text message body that you write in the visitor's voice.
    """
    sender_name = sender_name.strip()
    sender_email = sender_email.strip()
    if not sender_name or not EMAIL_PATTERN.match(sender_email) or not message.strip():
        return {"sent": False, "error": "A name, a valid email address and a message are required."}
    subject = subject.strip() or "Message from your website"

    api_key = os.getenv("BREVO_API_KEY")
    recipient = os.getenv("CONTACT_RECIPIENT_EMAIL", "pamuduranasinghe9@gmail.com")
    sender = os.getenv("CONTACT_SENDER_EMAIL", "pamudu123456789@gmail.com")
    if not api_key:
        logger.error("Contact email not sent: BREVO_API_KEY is not set.")
        return {"sent": False, "error": "Email delivery is not available right now. Nothing was sent."}

    body = (
        '<div style="font-family:Arial,sans-serif;line-height:1.6;color:#333;max-width:600px">'
        f"<p><strong>From:</strong> {html.escape(sender_name)} &lt;{html.escape(sender_email)}&gt;</p>"
        f"<p>{html.escape(message).replace(chr(10), '<br>')}</p>"
        '<hr style="border:none;border-top:1px solid #eee;margin-top:30px">'
        '<p style="color:#888;font-size:12px">Sent through the Virtual Pamudu assistant</p></div>'
    )
    payload = {
        "sender": {"email": sender, "name": SENDER_NAME},
        "to": [{"email": recipient, "name": "Pamudu"}],
        "replyTo": {"email": sender_email, "name": sender_name},
        "subject": f"[Virtual Pamudu] {subject}",
        "htmlContent": body,
    }
    try:
        response = httpx.post(
            BREVO_URL,
            json=payload,
            headers={"api-key": api_key, "accept": "application/json"},
            timeout=15,
        )
    except httpx.HTTPError as exc:
        logger.error("Contact email not sent: could not reach Brevo: %s", exc)
        return {"sent": False, "error": "The email service could not be reached. Nothing was sent."}

    if response.is_error:
        # Brevo's body says why (bad key, unrecognised IP, unverified sender).
        # It goes to the server log only, never to the visitor.
        logger.error("Contact email not sent: Brevo answered %s: %s", response.status_code, response.text[:500])
        return {"sent": False, "error": "The email service rejected the message. Nothing was sent."}
    return {"sent": True, "subject": subject, "from": sender_email}
