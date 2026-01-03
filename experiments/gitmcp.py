from mcp.server.fastmcp import FastMCP
from github import Github, Auth
import os
import dotenv

dotenv.load_dotenv()

# Initialize Server
mcp = FastMCP("Pamudu-Code-Reader")

# Auth (Modern approach - no deprecation warning)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("❌ Error: GITHUB_TOKEN is missing.")

g = Github(auth=Auth.Token(GITHUB_TOKEN))
USER = "pamudu123"

# --- TOOL 1: FIND THE REPO ---
@mcp.tool()
def search_my_repos(keyword: str) -> str:
    """
    Step 1: Find the right repository for the code question.
    Example: 'agent', 'finance', 'tracking'
    """
    query = f"user:{USER} {keyword} in:name"
    repos = g.search_repositories(query=query)
    
    results = []
    for repo in repos[:3]:
        results.append(f"Repo: '{repo.name}' (Description: {repo.description})")
        
    return "\n".join(results) if results else "No repositories found matching that keyword."

# --- TOOL 2: SEE THE MAP (File Structure) ---
@mcp.tool()
def get_file_structure(repo_name: str, path: str = "") -> str:
    """
    Step 2: List files in a folder to find where the code is.
    Leave 'path' empty to see the root folder.
    """
    try:
        repo = g.get_user(USER).get_repo(repo_name)
        contents = repo.get_contents(path)
        
        file_list = []
        for file in contents:
            type_icon = "📂" if file.type == "dir" else "📄"
            file_list.append(f"{type_icon} {file.path}")
            
        return "\n".join(file_list)
    except Exception as e:
        return f"❌ Error: Could not find path in {repo_name}. {e}"

# --- TOOL 3: READ THE CODE ---
@mcp.tool()
def read_file_content(repo_name: str, file_path: str) -> str:
    """
    Step 3: Read the actual code to answer the user's question.
    """
    try:
        repo = g.get_user(USER).get_repo(repo_name)
        file_content = repo.get_contents(file_path)
        
        # Decode bytes to string
        code = file_content.decoded_content.decode("utf-8")
        return code
    except Exception as e:
        return f"❌ Error reading file: {e}"

# --- TOOL 4: LIST ALL REPOS ---
@mcp.tool()
def list_all_repos(limit: int = 10) -> str:
    """
    Lists all repositories for the user.
    Useful when you don't know the exact repo name.
    Args: limit = number of repos to return (default 10)
    """
    try:
        repos = g.get_user(USER).get_repos(sort='updated', direction='desc')
        
        results = []
        count = 0
        for repo in repos:
            if count >= limit:
                break
            results.append(f"📦 {repo.name} - {repo.description or 'No description'}")
            results.append(f"   Updated: {repo.updated_at.strftime('%Y-%m-%d')}")
            count += 1
        
        if not results:
            return "No repositories found."
        
        return "\n".join(results)
    except Exception as e:
        return f"❌ Error listing repos: {e}"

# --- TOOL 5: SEARCH SPECIFIC REPO ---
@mcp.tool()
def find_repo_by_name(repo_name: str) -> str:
    """
    Search for a specific repository by exact or partial name match.
    Returns repo details if found.
    """
    try:
        # Try exact match first
        try:
            repo = g.get_user(USER).get_repo(repo_name)
            return f"""
✅ Found Repository: {repo.name}
--------------------------------
📝 Description: {repo.description or 'No description'}
🌟 Stars: {repo.stargazers_count}
🔱 Forks: {repo.forks_count}
📅 Created: {repo.created_at.strftime('%Y-%m-%d')}
📅 Updated: {repo.updated_at.strftime('%Y-%m-%d')}
🔗 URL: {repo.html_url}
"""
        except:
            # If exact match fails, try partial search
            all_repos = g.get_user(USER).get_repos()
            matches = []
            for repo in all_repos:
                if repo_name.lower() in repo.name.lower():
                    matches.append(f"📦 {repo.name} - {repo.description or 'No description'}")
            
            if matches:
                return "Partial matches found:\n" + "\n".join(matches[:5])
            else:
                return f"❌ No repository found matching '{repo_name}'"
    except Exception as e:
        return f"❌ Error: {e}"

if __name__ == "__main__":
    print("✅ Code Reader Agent is running (Pure Python)...")
    mcp.run()