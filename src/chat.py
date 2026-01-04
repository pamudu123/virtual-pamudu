"""
Virtual Pamudu Chat - Multi-turn Conversational Interface
A stateful chat system with conversation memory for coherent dialogues.
"""

import os
import operator
from typing import Annotated, TypedDict, Literal
from dotenv import load_dotenv

import structlog

# LangGraph Imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Import utilities
from utils import load_shortcut_keys, setup_logging

# Import tool logic
from tools.brain_tools import fetch_brain_context
from tools.medium_tools import list_medium_articles, get_medium_article_content, search_medium_articles
from tools.youtube_tools import list_youtube_videos, get_video_transcript, search_video_transcripts
from tools.github_tools import (
    list_my_repos, search_repos, get_repo_readme, 
    get_file_content, search_and_read_repo
)
from tools.mail_tool import send_simple_email

load_dotenv()

# Get logger (assuming setup_logging is called by app or main)
logger = structlog.get_logger()

# Load shortcut keys at module level for use as type
SHORTCUT_KEYS = load_shortcut_keys()
ShortcutKey = Literal[SHORTCUT_KEYS]  # type: ignore


# --- 1. DEFINE THE STATE (Shared Memory) ---
class AgentState(TypedDict):
    query: str
    # Conversation history for multi-turn coherence
    conversation_history: list[dict]  # [{"role": "user/assistant", "content": "..."}]
    # 'plan' is a list of search arguments (shortcuts/keywords)
    plan: list[dict]
    # 'results' is a list of strings found from the tools
    results: Annotated[list[str], operator.add]
    # Structured final response with citations
    final_answer: str
    citations: list[dict]


# --- 2. DEFINE THE MODEL & SCHEMA ---
def get_llm():
    """Lazy initialization of the LLM using OpenRouter."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    return ChatOpenAI(
        model="google/gemini-3-flash-preview", 
        temperature=0,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )


# We use Pydantic to force the LLM to return a structured Plan
class ToolParams(BaseModel):
    """Parameters for a tool call."""
    shortcuts: list[ShortcutKey] = Field(default_factory=list, description=f"Brain shortcuts: {', '.join(SHORTCUT_KEYS)}.")
    keywords: list[str] = Field(default_factory=list, description="Search keywords.")
    limit: int = Field(default=5, description="Max results to return.")
    repo_name: str = Field(default="", description="GitHub repository name.")
    file_path: str = Field(default="", description="Path to file in repo (e.g., 'src/main.py').")
    article_link: str = Field(default="", description="Medium article URL.")
    video_id: str = Field(default="", description="YouTube video ID.")
    state: str = Field(default="open", description="PR state: open, closed, all.")
    # Email params
    email_subject: str = Field(default="", description="Email subject line.")
    email_content: str = Field(default="", description="Email body content.")
    email_cc: str = Field(default="", description="CC email address (optional).")


class ToolCall(BaseModel):
    """A single tool call in the plan."""
    tool: str = Field(
        description="The tool to use: 'brain', 'medium', 'youtube', 'github', or 'email'."
    )
    action: str = Field(
        description="The specific action: 'search', 'list', 'get_content', 'get_transcript', 'get_readme', 'get_file', 'search_and_read', 'send'."
    )
    params: ToolParams = Field(
        default_factory=ToolParams,
        description="Parameters for the tool call."
    )


class AgentPlan(BaseModel):
    """The plan to retrieve information."""
    need_external_info: bool = Field(
        description="True if you need to fetch data, False if you can answer directly."
    )
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="List of tool calls to execute."
    )


class Citation(BaseModel):
    """A single citation/source reference."""
    source_type: str = Field(
        description="Type of source: 'brain', 'github', 'medium', 'youtube', 'email'"
    )
    source_name: str = Field(
        description="Name of the source (e.g., repo name, article title, file name)"
    )
    url: str = Field(
        default="",
        description="URL to the source if available"
    )


class AgentResponse(BaseModel):
    """Structured response from the agent with citations."""
    answer: str = Field(
        description="The main response text answering the user's query"
    )
    citations: list[Citation] = Field(
        default_factory=list,
        description="List of sources used to generate the answer"
    )


# --- 3. DEFINE NODES ---

def _format_conversation_history(history: list[dict]) -> str:
    """Format conversation history for context."""
    if not history:
        return ""
    
    formatted = []
    for msg in history:
        role = "User" if msg['role'] == 'user' else "Assistant"
        formatted.append(f"{role}: {msg['content']}")
    
    return "\n".join(formatted)


def planner_node(state: AgentState) -> dict:
    """
    NODE 1: Decides IF we need data and WHAT tools to use.
    Analyzes the user query with conversation history context.
    """
    log = logger.bind(node="planner")
    log.info("analyzing_query", query=state['query'])
    
    user_query = state['query']
    history = state.get('conversation_history', [])
    
    # Format conversation history for context
    history_context = _format_conversation_history(history)

    # System prompt with conversation awareness
    system_msg = """You are a research planner for Pamudu's personal AI assistant.

CONVERSATION CONTEXT:
You have access to the recent conversation history. Use it to:
1. Understand follow-up questions (e.g., "tell me more about that", "what else?")
2. Resolve pronouns and references to previous topics
3. Maintain context across multiple turns

You have access to 5 TOOLS:

## 1. BRAIN TOOL (Personal Knowledge Base)
- action: "search"
- params: {"shortcuts": [...], "keywords": [...]}
- shortcuts: "bio", "resume", "skills", "experience", "education", "projects", "awards"
- Use for: Who is Pamudu, his background, skills, work history, etc.

## 2. MEDIUM TOOL (Blog Articles)  
- action: "list" → params: {"limit": 5}
- action: "search" → params: {"keywords": [...]}
- action: "get_content" → params: {"article_link": "..."}
- Use for: What has Pamudu written, blog posts, articles, tutorials.

## 3. YOUTUBE TOOL (Videos & Transcripts)
- action: "list" → params: {"limit": 5}
- action: "search" → params: {"keywords": [...]}
- action: "get_transcript" → params: {"video_id": "..."}
- Use for: What videos has Pamudu made, video content, tutorials.

## 4. GITHUB TOOL (Code & Projects)
- action: "list" → params: {"limit": 10} (list repos)
- action: "search" → params: {"keywords": [...]} (search repos by keywords)
- action: "get_readme" → params: {"repo_name": "..."} (get README from main branch)
- action: "get_file" → params: {"repo_name": "...", "file_path": "..."} (get file from main branch)
- action: "search_and_read" → params: {"keywords": [...]} (search repo and read README)
- Use for: Pamudu's GitHub projects, code, repositories.

## 5. EMAIL TOOL (Send Emails)
- action: "send" → params: {"email_subject": "...", "email_content": "...", "email_cc": "..."}
- Emails are always sent to Pamudu
- Use for: Sending emails, notifications, summaries to Pamudu.

## RULES:
1. Use conversation history to understand context and follow-ups.
2. If user says "tell me more" or similar, infer the topic from history.
3. If query is about Pamudu (personal info, work, skills), use BRAIN tool.
4. If query is about articles/blog posts, use MEDIUM tool.
5. If query is about videos/video content, use YOUTUBE tool.
6. If query is about code/repos/GitHub activity, use GITHUB tool.
7. If query asks to send/email something, use EMAIL tool.
8. For general conversational responses or follow-ups that don't need new data, set need_external_info=False."""

    # Build messages with conversation history
    messages = [SystemMessage(content=system_msg)]
    
    if history_context:
        messages.append(HumanMessage(content=f"CONVERSATION HISTORY:\n{history_context}\n\nCURRENT QUERY: {user_query}"))
    else:
        messages.append(HumanMessage(content=user_query))

    # Use 'with_structured_output' to get JSON back reliably
    llm = get_llm()
    planner_llm = llm.with_structured_output(AgentPlan)
    plan = planner_llm.invoke(messages)

    log.info("plan_generated", need_info=plan.need_external_info, tool_calls=len(plan.tool_calls))
    for tc in plan.tool_calls:
        log.info("tool_plan", tool=tc.tool, action=tc.action, params=str(tc.params))

    # Convert to dicts for state storage
    calls_as_dicts = [tc.model_dump() for tc in plan.tool_calls] if plan.need_external_info else []

    return {"plan": calls_as_dicts}


def executor_node(state: AgentState) -> dict:
    """
    NODE 2: Runs the tool calls based on the plan.
    Executes searches against brain, Medium, YouTube, and GitHub.
    """
    log = logger.bind(node="executor")
    log.info("running_tools")
    
    tool_calls = state['plan']
    results = []

    for tc in tool_calls:
        tool = tc.get('tool', '')
        action = tc.get('action', '')
        params = tc.get('params', {})

        log.info("executing_tool", tool=tool, action=action, params=str(params))

        try:
            data = None
            
            # --- BRAIN TOOL ---
            if tool == 'brain':
                shortcuts = params.get('shortcuts', [])
                keywords = params.get('keywords', [])
                data = fetch_brain_context(shortcut_keys=shortcuts, search_keywords=keywords)
                
                if data:
                    for item in data:
                        source = item.get('source_path', 'unknown')
                        content = item.get('content', '')
                        results.append(f"--- BRAIN: {source} ---\n{content}\n")
                else:
                    results.append(f"--- BRAIN: No results for {params} ---\n")

            # --- MEDIUM TOOL ---
            elif tool == 'medium':
                if action == 'list':
                    limit = params.get('limit', 5)
                    data = list_medium_articles(limit=limit)
                    if data and 'error' not in data[0]:
                        formatted = "\n".join([f"• {a['title']} ({a['date']})\n  {a['link']}" for a in data])
                        results.append(f"--- MEDIUM: Latest Articles ---\n{formatted}\n")
                    else:
                        results.append(f"--- MEDIUM: Failed to list articles ---\n")
                        
                elif action == 'search':
                    keywords = params.get('keywords', [])
                    data = search_medium_articles(keywords=keywords)
                    if data and 'error' not in data[0]:
                        formatted = "\n".join([f"• {a['title']} (matches: {a['matches']})\n  {a['link']}" for a in data])
                        results.append(f"--- MEDIUM: Search Results ---\n{formatted}\n")
                    else:
                        results.append(f"--- MEDIUM: No articles matching {keywords} ---\n")
                        
                elif action == 'get_content':
                    link = params.get('article_link', '')
                    data = get_medium_article_content(link)
                    if 'error' not in data:
                        results.append(f"--- MEDIUM: {data['title']} ---\n{data['content']}\n")
                    else:
                        results.append(f"--- MEDIUM: {data['error']} ---\n")

            # --- YOUTUBE TOOL ---
            elif tool == 'youtube':
                if action == 'list':
                    limit = params.get('limit', 5)
                    data = list_youtube_videos(limit=limit)
                    if data and 'error' not in data[0]:
                        formatted = "\n".join([f"• {v['title']}\n  {v['link']}" for v in data])
                        results.append(f"--- YOUTUBE: Latest Videos ---\n{formatted}\n")
                    else:
                        results.append(f"--- YOUTUBE: Failed to list videos ---\n")
                        
                elif action == 'search':
                    keywords = params.get('keywords', [])
                    data = search_video_transcripts(keywords=keywords)
                    if data and 'error' not in data[0]:
                        formatted = "\n".join([f"• {v['title']} (matches: {v['matches']})\n  {v['link']}" for v in data])
                        results.append(f"--- YOUTUBE: Search Results ---\n{formatted}\n")
                    else:
                        results.append(f"--- YOUTUBE: No videos matching {keywords} ---\n")
                        
                elif action == 'get_transcript':
                    video_id = params.get('video_id', '')
                    data = get_video_transcript(video_id)
                    if 'error' not in data:
                        results.append(f"--- YOUTUBE TRANSCRIPT: {video_id} ---\n{data['transcript']}\n")
                    else:
                        results.append(f"--- YOUTUBE: {data['error']} ---\n")

            # --- GITHUB TOOL ---
            elif tool == 'github':
                if action == 'list':
                    limit = params.get('limit', 10)
                    data = list_my_repos(limit=limit)
                    if data and 'error' not in data[0]:
                        formatted = "\n".join([f"• {r['name']} ({r['language']}) ⭐{r['stars']}\n  {r['description'] or 'No description'}" for r in data])
                        results.append(f"--- GITHUB: Repositories ---\n{formatted}\n")
                    else:
                        results.append(f"--- GITHUB: Failed to list repos ---\n")
                        
                elif action == 'search':
                    keywords = params.get('keywords', [])
                    data = search_repos(keywords=keywords)
                    if data and 'error' not in data[0]:
                        formatted = "\n".join([f"• {r['name']} (matches: {r['matches']})\n  {r['url']}" for r in data])
                        results.append(f"--- GITHUB: Search Results ---\n{formatted}\n")
                    else:
                        results.append(f"--- GITHUB: No repos matching {keywords} ---\n")
                        
                elif action == 'get_readme':
                    repo_name = params.get('repo_name', '')
                    data = get_repo_readme(repo_name)
                    if 'error' not in data:
                        results.append(f"--- GITHUB README: {repo_name} (branch: {data['branch']}) ---\n{data['content']}\n")
                    else:
                        results.append(f"--- GITHUB: {data['error']} ---\n")
                        
                elif action == 'get_file':
                    repo_name = params.get('repo_name', '')
                    file_path = params.get('file_path', '')
                    data = get_file_content(repo_name, file_path)
                    if 'error' not in data:
                        results.append(f"--- GITHUB FILE: {repo_name}/{file_path} (branch: {data['branch']}) ---\n{data['content']}\n")
                    else:
                        results.append(f"--- GITHUB: {data['error']} ---\n")
                        
                elif action == 'search_and_read':
                    keywords = params.get('keywords', [])
                    data = search_and_read_repo(keywords=keywords)
                    if 'error' not in data:
                        repo_info = data['repo']
                        formatted = f"Found: {repo_info['name']}\nDescription: {repo_info['description']}\nURL: {repo_info['url']}\n\nREADME:\n{data['readme'] or 'No README'}"
                        results.append(f"--- GITHUB: Search & Read ---\n{formatted}\n")
                    else:
                        results.append(f"--- GITHUB: {data['error']} ---\n")

            # --- EMAIL TOOL ---
            elif tool == 'email':
                if action == 'send':
                    subject = params.get('email_subject', 'Message from Virtual Pamudu')
                    content = params.get('email_content', '')
                    cc_email = params.get('email_cc', '') or None
                    
                    # If content references previous results, include them
                    if not content or '[Will be filled' in content:
                        content = "\n".join(results) if results else "No content available."
                    
                    data = send_simple_email(
                        subject=subject,
                        message=content,
                        cc_email=cc_email
                    )
                    
                    if data.get('success'):
                        results.append(f"--- EMAIL: Sent successfully ---\nSubject: {subject}\nMessage ID: {data.get('message_id')}\n")
                    else:
                        results.append(f"--- EMAIL: Failed to send ---\nError: {data.get('error')}\n")

            else:
                log.error("unknown_tool", tool=tool)
                results.append(f"--- ERROR: Unknown tool '{tool}' ---\n")

        except Exception as e:
            log.error("tool_execution_failed", tool=tool, action=action, error=str(e))
            results.append(f"--- ERROR: {tool}.{action} failed: {str(e)} ---\n")

    log.info("results_found", count=len(results))
    return {"results": results}


def synthesizer_node(state: AgentState) -> dict:
    """
    NODE 3: Generates the final answer with structured citations.
    Uses conversation history for coherent responses.
    """
    log = logger.bind(node="synthesizer")
    log.info("generating_response")
    
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

    system_prompt = """You are Pamudu's personal AI assistant. 

CONVERSATION AWARENESS:
- You have access to the conversation history below
- Maintain coherence with previous exchanges
- Reference earlier topics naturally when relevant
- Use the conversation flow to provide more personalized responses

RULES:
1. Answer based on the provided context AND conversation history.
2. If context doesn't have new info, you can reference previous answers.
3. Be concise but informative.
4. Maintain a friendly, professional tone as if you're representing Pamudu.
5. For follow-up questions, build on your previous responses.

CITATIONS:
- Include citations for ALL sources you used from the NEW context.
- Extract the source_type from the context header (BRAIN, GITHUB, MEDIUM, YOUTUBE).
- Extract the source_name (file path, repo name, article title, video title).
- Extract the URL if present in the context.
- Only include citations for sources you actually referenced in your answer."""

    # Build the full context
    full_context = f"User Query: {query}\n\n"
    if history_context:
        full_context += f"--- CONVERSATION HISTORY ---\n{history_context}\n\n"
    full_context += f"--- RETRIEVED CONTEXT ---\n{context_block}"

    messages = [
        SystemMessage(content=system_prompt),
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
            "citations": []
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
        "citations": citations_as_dicts
    }


# --- 4. DEFINE CONDITIONAL EDGES ---

def should_search(state: AgentState) -> str:
    """
    Decides whether to go to Executor or straight to Synthesizer.
    Returns 'search' if plan has queries, 'skip' otherwise.
    """
    if not state.get('plan'):
        logger.info("skip_search")
        return "skip"
    return "search"


# --- 5. BUILD THE GRAPH ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)
workflow.add_node("synthesizer", synthesizer_node)

# Set Entry Point
workflow.set_entry_point("planner")

# Add Edges
workflow.add_conditional_edges(
    "planner",
    should_search,
    {
        "search": "executor",
        "skip": "synthesizer"
    }
)

workflow.add_edge("executor", "synthesizer")
workflow.add_edge("synthesizer", END)

# Compile the graph
app = workflow.compile()


# --- 6. CHAT SESSION CLASS ---

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
        # Kept these prints as they likely serve a UI purpose in some contexts, but internal logs are structural.
        # However, purely interactive logs are in start_chat(). These might be duplicate if used in CLI.
        # But app.py uses this class too. 
        # app.py calls chat(), and app.py doesn't want random prints to stdout if not needed.
        # So I will change these to logs as well, assuming start_chat handles the UI.
        
        log = logger.bind(user_message_length=len(user_message))
        log.info("processing_new_message")
        
        # Run the agent with conversation history
        inputs = {
            "query": user_message,
            "conversation_history": self.conversation_history.copy(),
            "results": [],
            "citations": []
        }
        result = app.invoke(inputs)
        
        answer = result.get('final_answer', 'No response generated.')
        citations = result.get('citations', [])
        
        # Update conversation history (no limit)
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": answer})
        
        log.info("message_complete", history_length=len(self.conversation_history) // 2)
        
        return {
            "answer": answer,
            "citations": citations,
            "history_length": len(self.conversation_history) // 2  # Number of turns
        }
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("history_cleared")
    
    def get_history(self) -> list[dict]:
        """Get the current conversation history."""
        return self.conversation_history.copy()


# --- 7. INTERACTIVE CHAT LOOP ---

def start_chat():
    """Start an interactive chat session."""
    # Ensure logging is set up if running standalone
    setup_logging()
    
    session = ChatSession()
    
    # Interaction UI - kept as prints
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
                print("🧹 Conversation history cleared.")  # UI feedback
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


# --- 8. MAIN ---

if __name__ == "__main__":
    start_chat()
