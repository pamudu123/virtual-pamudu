"""Contact tool: deliver a visitor's message to Pamudu by email (Brevo).

The recipient is fixed. Visitors can never choose where the email goes, and the
agent graph pauses for the visitor's explicit approval before this tool runs.
"""

import html
import re

from langchain_core.tools import tool

from .mailer import deliver_to_pamudu, wrap_html

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@tool
def send_message_to_pamudu(sender_name: str, sender_email: str, subject: str, message: str) -> dict:
    """Send a visitor's message to Pamudu's inbox.

    Call this once you have the visitor's name and email address (collect
    missing ones with the `ask_visitor` question panel, never in plain text).
    Write the subject and the message yourself from what the visitor has said;
    never ask them for a subject or for the wording. The chat shows your draft
    as an editable card and nothing is sent until the visitor presses Send, so
    do not ask "shall I send it?" yourself.

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

    body = wrap_html(
        f"<p><strong>From:</strong> {html.escape(sender_name)} &lt;{html.escape(sender_email)}&gt;</p>"
        f"<p>{html.escape(message).replace(chr(10), '<br>')}</p>"
    )
    error = deliver_to_pamudu(subject, body, reply_to={"email": sender_email, "name": sender_name})
    if error:
        return {"sent": False, "error": f"{error} Nothing was sent."}
    return {"sent": True, "subject": subject, "from": sender_email}
