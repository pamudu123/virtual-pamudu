from tools.mail_tool import send_email, send_simple_email

# Simple email (to default recipient)
result = send_simple_email(
    subject="Hello from AI",
    message="This is a test message.",
    cc_email=None  # or "someone@example.com"
)

# Full control
result = send_email(
    subject="Custom Email",
    content="<h1>Hello!</h1><p>HTML content here</p>",
    to_email="pamuduranasinghe9@gmail.com",
    cc_email=None,
    is_html=True
)

print(result)