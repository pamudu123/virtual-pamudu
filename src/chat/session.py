"""
ChatSession class for managing stateful conversations.
"""

import structlog

from .graph import app

logger = structlog.get_logger()


class ChatSession:
    """
    A stateful chat session that maintains conversation history.
    """
    
    def __init__(self):
        """Initialize a new chat session."""
        self.conversation_history: list[dict] = []
    
    def chat(self, user_message: str) -> dict:
        """
        Send a message and get a response.
        
        Args:
            user_message: The user's message.
            
        Returns:
            Dict with 'answer', 'citations', and 'history_length'.
        """
        log = logger.bind(user_message_length=len(user_message))
        log.info("processing_new_message")
        
        # Run the agent with conversation history
        inputs = {
            "query": user_message,
            "conversation_history": self.conversation_history.copy(),
            "results": [],
            "citations": [],
            "suggested_questions": []
        }
        result = app.invoke(inputs)
        
        answer = result.get('final_answer', 'No response generated.')
        citations = result.get('citations', [])
        suggested_questions = result.get('suggested_questions', [])
        
        # Update conversation history (no limit)
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": answer})
        
        log.info("message_complete", history_length=len(self.conversation_history) // 2)
        
        return {
            "answer": answer,
            "citations": citations,
            "suggested_questions": suggested_questions,
            "history_length": len(self.conversation_history) // 2  # Number of turns
        }
    
    def chat_stream(self, user_message: str):
        """
        Stream the agent's execution steps and final response.
        Yields generator of status updates and final result.
        """
        log = logger.bind(user_message_length=len(user_message))
        log.info("processing_new_message_stream")
        
        inputs = {
            "query": user_message,
            "conversation_history": self.conversation_history.copy(),
            "results": [],
            "citations": [],
            "suggested_questions": []
        }
        
        final_answer = ""
        
        # 1. Yield Initial Status
        yield {"type": "status", "node": "start", "message": "🧠 Analyzing request..."}
        
        # 2. Iterate through Graph Steps
        for output in app.stream(inputs):
            for node_name, state_update in output.items():
                # Guard against None state_update
                if state_update is None:
                    state_update = {}
                
                if node_name == "planner":
                    plan = state_update.get("plan", [])
                    # Capture final_answer if planner provides it directly
                    planner_answer = state_update.get("final_answer", "")
                    if planner_answer:
                        final_answer = planner_answer
                    
                    if plan:
                        tool_names = [t.get('tool') for t in plan]
                        actions = [t.get('action') for t in plan]
                        # Create a nice message like "Searching GitHub, Reading Medium..."
                        details = []
                        for t, a in zip(tool_names, actions):
                            if t == 'github': details.append("GitHub")
                            elif t == 'medium': details.append("Medium")
                            elif t == 'youtube': details.append("YouTube")
                            elif t == 'brain': details.append("Brain")
                            elif t == 'email': details.append("Email")
                        
                        unique_tools = list(set(details))
                        msg = f"🔎 Using tools: {', '.join(unique_tools)}..."
                        yield {"type": "status", "node": "planner", "message": msg}
                    else:
                        yield {"type": "status", "node": "planner", "message": "📝 Thinking..."}
                        
                elif node_name == "executor":
                    results = state_update.get("results", [])
                    msg = f"📊 Analyzed {len(results)} search results."
                    yield {"type": "status", "node": "executor", "message": msg}
                    yield {"type": "status", "node": "synthesizer", "message": "✍️ Drafting response..."}
                    
                elif node_name == "synthesizer":
                    # Synthesizer may return empty dict if using planner response
                    synth_answer = state_update.get("final_answer", "")
                    citations = state_update.get("citations", [])
                    suggested_questions = state_update.get("suggested_questions", [])
                    
                    # Use synthesizer answer if available, otherwise use captured planner answer
                    if synth_answer:
                        final_answer = synth_answer
                    
                    # Final Result
                    yield {
                        "type": "result",
                        "answer": final_answer,
                        "citations": citations,
                        "suggested_questions": suggested_questions,
                        "history_length": len(self.conversation_history) // 2 + 1
                    }
                    
        # 3. Update History
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": final_answer})
        
        log.info("message_stream_complete")

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("history_cleared")
    
    def get_history(self) -> list[dict]:
        """Get the current conversation history."""
        return self.conversation_history.copy()


# Initial suggestions for the UI before any conversation
INITIAL_SUGGESTIONS = [
    "Who is Pamudu?",
    "What are Pamudu's skills?",
    "Show me Pamudu's projects"
]


def get_initial_suggestions() -> list[str]:
    """Get initial starter suggestions to display in UI."""
    return INITIAL_SUGGESTIONS.copy()
