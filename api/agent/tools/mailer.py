"""Email delivery to Pamudu's inbox (Brevo).

The recipient is fixed here. No tool or visitor can choose where mail goes.
"""

import logging
import os

import httpx

logger = logging.getLogger(__name__)

BREVO_URL = "https://api.brevo.com/v3/smtp/email"
SENDER_NAME = "Virtual Pamudu"
FOOTER = (
    '<hr style="border:none;border-top:1px solid #eee;margin-top:30px">'
    '<p style="color:#888;font-size:12px">Sent through the Virtual Pamudu assistant</p>'
)


def wrap_html(inner: str) -> str:
    """Put an email's content in the shared frame and footer."""
    return (
        '<div style="font-family:Arial,sans-serif;line-height:1.6;color:#333;max-width:600px">'
        f"{inner}{FOOTER}</div>"
    )


def deliver_to_pamudu(subject: str, html_body: str, reply_to: dict | None = None) -> str | None:
    """Send one email to Pamudu.

    Returns None when Brevo accepted it, otherwise a short reason that is safe
    to show a visitor. The real cause (bad key, unrecognised IP, unverified
    sender) goes to the server log only.
    """
    api_key = os.getenv("BREVO_API_KEY")
    recipient = os.getenv("CONTACT_RECIPIENT_EMAIL", "pamuduranasinghe9@gmail.com")
    sender = os.getenv("CONTACT_SENDER_EMAIL", "pamudu123456789@gmail.com")
    if not api_key:
        logger.error("Email not sent: BREVO_API_KEY is not set.")
        return "Email delivery is not available right now."

    payload = {
        "sender": {"email": sender, "name": SENDER_NAME},
        "to": [{"email": recipient, "name": "Pamudu"}],
        "subject": f"[Virtual Pamudu] {subject}",
        "htmlContent": html_body,
    }
    if reply_to:
        payload["replyTo"] = reply_to
    try:
        response = httpx.post(
            BREVO_URL,
            json=payload,
            headers={"api-key": api_key, "accept": "application/json"},
            timeout=15,
        )
    except httpx.HTTPError as exc:
        logger.error("Email not sent: could not reach Brevo: %s", exc)
        return "The email service could not be reached."

    if response.is_error:
        logger.error("Email not sent: Brevo answered %s: %s", response.status_code, response.text[:500])
        return "The email service rejected the message."
    return None
