import os
import operator
from typing import Annotated, TypedDict, Literal, Union
from dotenv import load_dotenv

import operator

# LangGraph Imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Import utilities
from utils import load_shortcut_keys
from typing import Literal

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

# Load shortcut keys at module level for use as type
SHORTCUT_KEYS = load_shortcut_keys()
ShortcutKey = Literal[SHORTCUT_KEYS]  # type: ignore

# --- 1. DEFINE THE STATE (Shared Memory) ---
class AgentState(TypedDict):
    query: str
    # 'plan' is a list of search arguments (shortcuts/keywords)
    plan: list[dict]
    # 'results' is a list of strings found from the tools
    results: Annotated[list[str], operator.add]
    # Structured final response with citations
    final_answer: str
    citations: list[dict]


# --- 2. DEFINE THE MODEL & SCHEMA ---
def get_llm():
    """Lazy initialization of the LLM to avoid import-time failures."""
    return ChatOpenAI(model="gpt-5.1", temperature=0)


# We use Pydantic to force the LLM to return a structured Plan
class SearchParams(BaseModel):
    """Parameters for search/retrieval tools (brain, medium, youtube, github)."""
    shortcuts: list[ShortcutKey] = Field(default_factory=list, description=f"Brain shortcuts: {', '.join(SHORTCUT_KEYS)}.")
    keywords: list[str] = Field(default_factory=list, description="Search keywords.")
    limit: int = Field(default=5, description="Max results to return.")
    repo_name: str = Field(default="", description="GitHub repository name.")
    file_path: str = Field(default="", description="Path to file in repo (e.g., 'src/main.py').")
    article_link: str = Field(default="", description="Medium article URL.")
    video_id: str = Field(default="", description="YouTube video ID.")
    state: str = Field(default="open", description="PR state: open, closed, all.")


class EmailParams(BaseModel):
    """Parameters for sending an email."""
    email_subject: str = Field(description="Email subject line.")
    email_content: str = Field(description="Email body content.")
    email_cc: str = Field(default="", description="CC email address (optional).")


class ToolCall(BaseModel):
    """A single tool call in the plan."""
    tool: str = Field(
        description="The tool to use: 'brain', 'medium', 'youtube', 'github', or 'email'."
    )
    action: str = Field(
        description="The specific action: 'search', 'list', 'get_content', 'get_status', 'get_transcript', 'get_readme', 'list_prs', 'check_reviews', 'send'."
    )
    params: Union[SearchParams, EmailParams] = Field(
        description="Parameters for the tool call. Use EmailParams for 'email' tool, SearchParams for others."
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

def planner_node(state: AgentState) -> dict:
    """
    NODE 1: Decides IF we need data and WHAT tools to use.
    Analyzes the user query and generates a plan with tool calls.
    """
    print("🤔 Planner: Analyzing query...")
    user_query = state['query']

    # System prompt to guide the planning
    system_msg = """You are Pamudu's AI Assistant. Help to answer the other's queries on Pamudu to get other know better about Pamudu.

You have access to 4 TOOLS:

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
- email_cc is optional (can be empty string)
- Use for: Sending emails, notifications, summaries to Pamudu.

## RULES:
1. If query is about Pamudu (personal info, work, skills), use BRAIN tool.
2. If query is about articles/blog posts, use MEDIUM tool.
3. If query is about videos/video content, use YOUTUBE tool.
4. If query is about code/repos/GitHub activity, use GITHUB tool.
5. If query asks to send/email something, use EMAIL tool.
6. You can use MULTIPLE tools if the query spans multiple areas.
7. For general knowledge questions (not about Pamudu), set need_external_info=False.

## EXAMPLES:

Query: "Who is Pamudu and what has he written about AI?"
{
  "need_external_info": true,
  "tool_calls": [
    {"tool": "brain", "action": "search", "params": {"shortcuts": ["bio"], "keywords": []}},
    {"tool": "medium", "action": "search", "params": {"keywords": ["AI", "artificial intelligence"]}}
  ]
}

Query: "Show me Pamudu's latest YouTube videos"
{
  "need_external_info": true,
  "tool_calls": [
    {"tool": "youtube", "action": "list", "params": {"limit": 5}}
  ]
}

Query: "What GitHub projects does Pamudu have about machine learning?"
{
  "need_external_info": true,
  "tool_calls": [
    {"tool": "github", "action": "search", "params": {"keywords": ["machine learning", "ml", "AI"]}}
  ]
}

Query: "Send me an email with Pamudu's bio"
{
  "need_external_info": true,
  "tool_calls": [
    {"tool": "brain", "action": "search", "params": {"shortcuts": ["bio"]}},
    {"tool": "email", "action": "send", "params": {"email_subject": "Pamudu's Bio", "email_content": "[Will be filled with bio content]", "email_cc": ""}}
  ]
}"""

    # Use 'with_structured_output' to get JSON back reliably
    llm = get_llm()
    planner_llm = llm.with_structured_output(AgentPlan)
    plan = planner_llm.invoke([
        SystemMessage(content=system_msg),
        HumanMessage(content=user_query)
    ])

    print(f"   📋 Plan: need_info={plan.need_external_info}, calls={len(plan.tool_calls)}")
    for tc in plan.tool_calls:
        print(f"      → {tc.tool}.{tc.action}({tc.params})")

    # Convert to dicts for state storage
    calls_as_dicts = [tc.model_dump() for tc in plan.tool_calls] if plan.need_external_info else []

    return {"plan": calls_as_dicts}


def executor_node(state: AgentState) -> dict:
    """
    NODE 2: Runs the tool calls based on the plan.
    Executes searches against brain, Medium, YouTube, and GitHub.
    """
    print("⚡ Executor: Running tools...")
    tool_calls = state['plan']
    results = []

    for tc in tool_calls:
        tool = tc.get('tool', '')
        action = tc.get('action', '')
        params = tc.get('params', {})

        print(f"   ▶️ {tool}.{action}({params})")

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
                        # Use accumulated results as content
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
                results.append(f"--- ERROR: Unknown tool '{tool}' ---\n")

        except Exception as e:
            results.append(f"--- ERROR: {tool}.{action} failed: {str(e)} ---\n")

    print(f"   ✅ Found {len(results)} result(s)")
    return {"results": results}


def synthesizer_node(state: AgentState) -> dict:
    """
    NODE 3: Generates the final answer with structured citations.
    Reads the fetched content and responds to the user.
    """
    print("🧠 Synthesizer: Generating response...")
    query = state['query']
    results = state.get('results', [])

    # Create the context block
    if results:
        context_block = "\n".join(results)
    else:
        context_block = "No search results available. Answer based on general knowledge if possible, or indicate that you don't have specific information about Pamudu."

    messages = [
        SystemMessage(content="""You are Pamudu's AI Assistant. You are NOT Pamudu himself, but his intelligent digital representative.

CORE PERSONA:
- Name: Pamudu's AI Assistant
- Tone: Professional, warm, helpful, and "human-kind".
- Style: Conversational but concise. Avoid robotic phrasing (e.g., "I have retrieved..."). Instead use "I found...", "Here is...", "It looks like...".

RULES:
1. **ANSWER GENERATION**:
   - Answer based ONLY on the provided context if it contains relevant info.
   - If the answer isn't in the context, say "I don't have that specific information in my knowledge base right now."
   - Do NOT hallucinate or make up facts about Pamudu.

2. **STRUCTURE & FORMATTING**:
   - Use Markdown for clarity (bolding, bullet points).
   - Break down complex answers into digestible sections.
   - Keep paragraphs short (2-3 sentences max).

3. **EMAIL DRAFTING (Strict)**:
   - If asked to draft an email, do NOT use placeholders like "[Name]" or "[Date]".
   - If details are missing, ASK the user for them before drafting.
   - Always confirm: "Does this look good to send?"

CITATIONS:
- Include citations for ALL sources you used from the context.
- Extract the source_type from the context header (BRAIN, GITHUB, MEDIUM, YOUTUBE).
- Extract the source_name (file path, repo name, article title, video title).
- Extract the URL if present in the context.
- Only include citations for sources you actually referenced in your answer."""),
        HumanMessage(content=f"User Query: {query}\n\n--- RETRIEVED CONTEXT ---\n{context_block}")
    ]

    llm = get_llm()
    structured_llm = llm.with_structured_output(AgentResponse)
    response = structured_llm.invoke(messages)
    
    # Convert citations to dicts for state storage
    citations_as_dicts = [c.model_dump() for c in response.citations]
    
    print(f"   📚 Citations: {len(citations_as_dicts)} source(s)")
    for c in response.citations:
        print(f"      → [{c.source_type}] {c.source_name}")
    
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
        print("⏭️  No search needed. Skipping to synthesizer.")
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
# Planner -> (Condition) -> Executor OR Synthesizer
workflow.add_conditional_edges(
    "planner",
    should_search,
    {
        "search": "executor",
        "skip": "synthesizer"  # If no search needed, go to synthesizer
    }
)

# Executor -> Synthesizer
workflow.add_edge("executor", "synthesizer")

# Synthesizer -> End
workflow.add_edge("synthesizer", END)

# Compile the graph
app = workflow.compile()


# --- 6. PUBLIC INTERFACE ---

def run_agent(query: str) -> dict:
    """
    Run the agent with a user query.
    
    Args:
        query: The user's question or request.
        
    Returns:
        Dict with 'answer' (str) and 'citations' (list of dicts).
        Each citation has: source_type, source_name, url
    """
    print(f"\n{'='*60}")
    print(f"💬 User: {query}")
    print('='*60)

    inputs = {"query": query, "results": [], "citations": []}
    result = app.invoke(inputs)

    return {
        "answer": result.get('final_answer', 'No response generated.'),
        "citations": result.get('citations', [])
    }


# --- 7. MAIN (TESTING) ---

if __name__ == "__main__":
    # Test queries covering all tools
    test_queries = [
        "Who is Pamudu?",  # Brain only
        "What articles has Pamudu written about AI?",  # Medium
        "Show me Pamudu's latest YouTube videos",  # YouTube
        "What GitHub repos does Pamudu have?",  # GitHub
    ]

    for query in test_queries:  # Run first query for quick test
        response = run_agent(query)
        print(f"\n🤖 Final Answer:\n{response['answer']}")
        
        if response['citations']:
            print(f"\n📚 Sources ({len(response['citations'])}):")
            for c in response['citations']:
                if c.get('url'):
                    print(f"   • [{c['source_type']}] {c['source_name']}")
                    print(f"     {c['url']}")
                else:
                    print(f"   • [{c['source_type']}] {c['source_name']}")
        
        print("\n" + "="*60 + "\n")

