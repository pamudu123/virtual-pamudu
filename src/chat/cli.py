"""
Interactive CLI for the chat agent.
"""

import structlog

from .session import ChatSession
from utils import setup_logging

logger = structlog.get_logger()


def start_chat():
    """Start an interactive chat session."""
    # Ensure logging is set up if running standalone
    setup_logging()
    
    session = ChatSession()
    
    # Interaction UI
    print("\n" + "="*60)
    print("🤖 Virtual Pamudu Chat")
    print("="*60)
    print("Type your questions below. Commands:")
    print("  /clear  - Clear conversation history")
    print("  /history - Show conversation history")
    print("  /quit   - Exit the chat")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() == '/quit':
                print("\n👋 Goodbye!")
                break
            
            elif user_input.lower() == '/clear':
                session.clear_history()
                print("🧹 Conversation history cleared.")
                continue
            
            elif user_input.lower() == '/history':
                history = session.get_history()
                if not history:
                    print("📜 No conversation history yet.")
                else:
                    print("\n📜 Conversation History:")
                    for i, msg in enumerate(history):
                        role = "You" if msg['role'] == 'user' else "Bot"
                        print(f"  [{role}]: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
                    print()
                continue
            
            # Regular chat
            response = session.chat(user_input)
            
            print(f"\n🤖 Assistant: {response['answer']}")
            
            if response['citations']:
                print(f"\n📚 Sources ({len(response['citations'])}):")
                for c in response['citations']:
                    if c.get('url'):
                        print(f"   • [{c['source_type']}] {c['source_name']}")
                        print(f"     {c['url']}")
                    else:
                        print(f"   • [{c['source_type']}] {c['source_name']}")
            
            print(f"\n[Turn {response['history_length']}]")
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error("chat_loop_error", error=str(e))
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.\n")
