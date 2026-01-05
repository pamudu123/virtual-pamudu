"""
Email Tools - Send emails using Brevo (Sendinblue) API.
"""

import os
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

load_dotenv()

# --- CONFIGURATION ---
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
DEFAULT_RECIPIENT = "pamuduranasinghe9@gmail.com"
DEFAULT_SENDER_EMAIL = "pamudu123456789@gmail.com"  # Must be verified in Brevo
DEFAULT_SENDER_NAME = "Virtual Pamudu"


def send_email(
    subject: str,
    content: str,
    to_email: str = DEFAULT_RECIPIENT,
    to_name: str = "Pamudu",
    cc_email: str | None = None,
    cc_name: str | None = None,
    sender_email: str = DEFAULT_SENDER_EMAIL,
    sender_name: str = DEFAULT_SENDER_NAME,
    is_html: bool = True
) -> dict:
    """
    Send an email using Brevo API.
    
    Args:
        subject: Email subject line.
        content: Email body (HTML or plain text).
        to_email: Recipient email address.
        to_name: Recipient name.
        cc_email: CC email address (optional).
        cc_name: CC recipient name (optional).
        sender_email: Sender email (must be verified in Brevo).
        sender_name: Sender display name.
        is_html: If True, content is HTML; if False, plain text.
        
    Returns:
        Dict with status and message_id or error.
    """
    
    try:
        # Configure API key
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = BREVO_API_KEY
        
        # Create API instance
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        # Build recipient list
        to_list = [{"email": to_email, "name": to_name}]
        
        # Build CC list if provided
        cc_list = None
        if cc_email:
            cc_list = [{"email": cc_email, "name": cc_name or cc_email}]
        
        # Create email object
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to_list,
            cc=cc_list,
            sender={"email": sender_email, "name": sender_name},
            subject=subject,
            html_content=content if is_html else None,
            text_content=content if not is_html else None
        )
        
        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)
        
        return {
            "success": True,
            "message_id": api_response.message_id,
            "to": to_email,
            "cc": cc_email,
            "subject": subject
        }
        
    except ApiException as e:
        return {"error": f"Brevo API error: {e.reason}", "status": e.status}
    except Exception as e:
        return {"error": f"Failed to send email: {str(e)}"}


def send_simple_email(subject: str, message: str, cc_email: str | None = None) -> dict:
    """
    Simplified email sending to default recipient.
    
    Args:
        subject: Email subject.
        message: Email message (plain text, will be wrapped in HTML).
        cc_email: Optional CC email address.
        
    Returns:
        Dict with status.
    """
    # Wrap plain text in simple HTML
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            {message.replace(chr(10), '<br>')}
            <hr style="margin-top: 30px; border: none; border-top: 1px solid #eee;">
            <p style="color: #888; font-size: 12px;">
                Sent by Virtual Pamudu AI Assistant
            </p>
        </div>
    </body>
    </html>
    """
    
    return send_email(
        subject=subject,
        content=html_content,
        cc_email=cc_email,
        is_html=True
    )


# --- TESTING ---
if __name__ == "__main__":
    print("📧 Testing Email Tools...")
    
    # Check if API key is set
    if not BREVO_API_KEY:
        print("⚠️  BREVO_API_KEY not set in .env file")
        print("   Add: BREVO_API_KEY=your-api-key-here")
    else:
        print(f"✅ API key found (ends with: ...{BREVO_API_KEY[-4:]})")
        
        # Test send (uncomment to actually send)
        # result = send_simple_email(
        #     subject="Test from Virtual Pamudu",
        #     message="This is a test email sent from the Virtual Pamudu AI assistant.",
        #     cc_email=None
        # )
        # print(f"Result: {result}")
