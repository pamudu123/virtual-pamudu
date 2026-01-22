"""
Executor node for the chat agent.
Runs tool calls based on the plan from the planner.
"""

import structlog

from ..schemas import AgentState

# Import tool logic
from tools.brain_tools import fetch_brain_context
from tools.medium_tools import list_medium_articles, get_medium_article_content, search_medium_articles
from tools.youtube_tools import list_youtube_videos, get_video_transcript, search_video_transcripts
from tools.github_tools import (
    list_my_repos, search_repos, get_repo_readme, 
    get_file_content, search_and_read_repo
)
from tools.mail_tool import send_email

logger = structlog.get_logger()


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
                    email_to = params.get('email_to', '')
                    subject = params.get('email_subject', 'Message from Virtual Pamudu')
                    content = params.get('email_content', '')
                    cc_email = params.get('email_cc', '') or None
                    
                    # If content references previous results, include them
                    if not content or '[Will be filled' in content:
                        content = "\n".join(results) if results else "No content available."
                    
                    if not email_to:
                        results.append(f"--- EMAIL: Failed to send ---\nError: No 'to_email' specified.\n")
                    else:
                        data = send_email(
                            to_email=email_to,
                            subject=subject,
                            content=content,
                            cc_email=cc_email,
                            is_html=True
                        )
                        
                        if data.get('success'):
                            results.append(f"--- EMAIL: Sent successfully ---\nTo: {email_to}\nSubject: {subject}\nMessage ID: {data.get('message_id')}\n")
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
