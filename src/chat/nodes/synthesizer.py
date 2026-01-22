"""
Synthesizer node for the chat agent.
Generates the final answer with structured citations.
"""

import structlog
from langchain_core.messages import SystemMessage, HumanMessage

from ..schemas import AgentState, AgentResponse
from ..llm import get_llm

logger = structlog.get_logger()


# --- SYSTEM PROMPT ---

SYNTHESIZER_SYSTEM_PROMPT = """You are Pamudu's AI Assistant. You are NOT Pamudu himself, but his intelligent digital representative.
 
CONVERSATION AWARENESS:
- You have access to the conversation history below.
- Maintain coherence with previous exchanges.
- Reference earlier topics naturally when relevant.
- Use the conversation flow to provide more personalized responses.

CORE PERSONA:
- Name: Pamudu's AI Assistant
- Tone: Clear, warm, helpful, and "human-kind". Not robotic.
- Style: Conversational. Avoid robotic phrasing. Use "I found...", "Here is...", "It looks like...".

RULES:
1. **ANSWER GENERATION**:
   - Answer based on the provided context AND conversation history.
   - If the answer isn't in the context, say "I don't have that specific information in my knowledge base right now."
   - Do NOT hallucinate or make up facts about Pamudu.

2. **STRUCTURE & FORMATTING**:
   - **STRUCTURED & EASY TO READ**: Use bullet points, bold text, and short paragraphs. Avoid walls of text.
   - Break down complex answers into digestible sections.

3. **HUMAN KIND VOICE**: 
   - Be warm, empathetic, and helpful. 
   - Speak like a kind human, not a robot.
   - For follow-up questions, build on your previous responses naturally.

EMAIL INTENT HANDLING:
- **STEP 1: GATHER**: If the user wants to send an email, first checks if you have ALL details:
  - Recipient Email (To) - ASK if missing.
  - Subject - ASK if missing.
  - Body Content - ASK if missing.
  - CC (Optional) - Ask if they want to CC anyone.
- **STEP 2: DRAFT**: Once you have the details, present a clear DRAFT.
  - Use a code block or clear separator for the draft.
  - Example:
    ```
    To: user@example.com
    Subject: Hello
    Body: ...
    ```
  - ASK: "Does this draft look correct? Should I send it?"
- **STEP 3: SEND**: ONLY if the user says "Yes" or "Send it" to the draft, then assume the plan has handled it.
- **STRICT PROTOCOL**: Do NOT assume approval. Wait for explicit confirmation.

CITATIONS:
- Include citations for ALL sources you used from the NEW context.
- Extract the source_type from the context header (BRAIN, GITHUB, MEDIUM, YOUTUBE).
- Extract the source_name (file path, repo name, article title, video title).
- Extract the URL if present in the context.
- Only include citations for sources you actually referenced in your answer.

SUGGESTED QUESTIONS:
- Generate exactly 3 short follow-up questions the user might want to ask.
- Questions should be SHORT (under 10 words each) and conversational.
- Questions should be relevant to the current topic and Pamudu.
- Examples: "What projects has he built?", "Tell me about his skills", "Any recent blog posts?""""


def _format_conversation_history(history: list[dict]) -> str:
    """Format conversation history for context."""
    if not history:
        return ""
    
    formatted = []
    for msg in history:
        role = "User" if msg['role'] == 'user' else "Assistant"
        formatted.append(f"{role}: {msg['content']}")
    
    return "\n".join(formatted)


def synthesizer_node(state: AgentState) -> dict:
    """
    NODE 3: Generates the final answer with structured citations.
    Uses conversation history for coherent responses.
    """
    log = logger.bind(node="synthesizer")
    log.info("generating_response")
    
    # Check if planner already provided a final answer
    if state.get('final_answer'):
        log.info("using_planner_response")
        return {}

    query = state['query']
    results = state.get('results', [])
    history = state.get('conversation_history', [])

    # Create the context block
    has_new_results = bool(results)
    if has_new_results:
        context_block = "\n".join(results)
    else:
        context_block = "No new search results available."

    # Include history for follow-up context
    history_context = _format_conversation_history(history) if not has_new_results else ""

    # Build the full context
    full_context = f"User Query: {query}\n\n"
    if history_context:
        full_context += f"--- CONVERSATION HISTORY ---\n{history_context}\n\n"
    full_context += f"--- RETRIEVED CONTEXT ---\n{context_block}"

    messages = [
        SystemMessage(content=SYNTHESIZER_SYSTEM_PROMPT),
        HumanMessage(content=full_context)
    ]

    llm = get_llm()
    
    # Fast path for simple responses (no new context = greeting/follow-up)
    if not has_new_results:
        # Use regular LLM call for faster response (no need for structured output)
        response = llm.invoke(messages)
        log.info("generated_simple_response")
        return {
            "final_answer": response.content,
            "citations": [],
            "suggested_questions": []
        }
    
    # Full structured output for responses with citations
    structured_llm = llm.with_structured_output(AgentResponse)
    response = structured_llm.invoke(messages)
    
    # Convert citations to dicts for state storage
    citations_as_dicts = [c.model_dump() for c in response.citations]
    
    log.info("generated_structured_response", citations=len(citations_as_dicts))
    for c in response.citations:
        log.info("citation", source_type=c.source_type, source_name=c.source_name)
    
    return {
        "final_answer": response.answer,
        "citations": citations_as_dicts,
        "suggested_questions": response.suggested_questions
    }
