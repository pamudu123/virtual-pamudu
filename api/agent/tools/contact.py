"""Contact tool: deliver a visitor's message to Pamudu by email (Brevo).

The recipient is fixed. Visitors can never choose where the email goes, and the
agent graph pauses for the visitor's explicit approval before this tool runs.
"""

import html
import os

import httpx
from langchain_core.tools import tool

BREVO_URL = "https://api.brevo.com/v3/smtp/email"
SENDER_NAME = "Virtual Pamudu"


@tool
def send_message_to_pamudu(sender_name: str, sender_email: str, subject: str, message: str) -> dict:
    """Send a visitor's message to Pamudu's inbox.

    Only call this once you have the visitor's name, their email address, a
    subject and the message. The visitor reviews and approves the draft in the
    chat before anything is sent, so do not ask "shall I send it?" yourself.

    Args:
        sender_name: The visitor's name.
        sender_email: The visitor's email address, used as reply-to.
        subject: Subject line.
        message: Plain-text message body.
    """
    api_key = os.getenv("BREVO_API_KEY")
    recipient = os.getenv("CONTACT_RECIPIENT_EMAIL", "pamuduranasinghe9@gmail.com")
    sender = os.getenv("CONTACT_SENDER_EMAIL", "pamudu123456789@gmail.com")
    if not api_key:
        return {"error": "Email is not configured on this server."}

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
        response.raise_for_status()
        return {"sent": True, "subject": subject, "from": sender_email}
    except httpx.HTTPError as exc:
        return {"error": f"The message could not be sent: {exc}"}
