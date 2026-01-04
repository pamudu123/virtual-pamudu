"""
GitHub Tools - Fetch repository info and content from GitHub.
Simplified for virtual assistant: search repos and read content from main branch.
"""

import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USER = "pamudu123"

# Initialize GitHub client (lazy)
_github_client = None


def _get_github() -> Github:
    """Lazy initialization of GitHub client."""
    global _github_client
    if _github_client is None:
        if not GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN not found in environment")
        _github_client = Github(GITHUB_TOKEN)
    return _github_client


def list_my_repos(limit: int = 10) -> list[dict]:
    """
    List repositories owned by the user.
    
    Args:
        limit: Maximum number of repos to return.
        
    Returns:
        List of repository metadata.
    """
    try:
        g = _get_github()
        user = g.get_user(USER)
        repos = user.get_repos(sort='updated')
        
        result = []
        for repo in repos[:limit]:
            result.append({
                "name": repo.name,
                "description": repo.description,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "updated": str(repo.updated_at),
                "url": repo.html_url
            })
        
        return result
        
    except Exception as e:
        return [{"error": f"Failed to list repos: {str(e)}"}]


def search_repos(keywords: list[str], limit: int = 5) -> list[dict]:
    """
    Search user's repositories by keywords in name/description.
    
    Args:
        keywords: List of keywords to search.
        limit: Maximum results.
        
    Returns:
        List of matching repositories.
    """
    try:
        repos = list_my_repos(limit=50)  # Get more to search through
        
        if repos and 'error' in repos[0]:
            return repos
        
        keywords_lower = [k.lower() for k in keywords]
        results = []
        
        for repo in repos:
            name_lower = repo['name'].lower()
            desc_lower = (repo['description'] or '').lower()
            
            matches = []
            for kw in keywords_lower:
                if kw in name_lower:
                    matches.append(f"name:{kw}")
                if kw in desc_lower:
                    matches.append(f"desc:{kw}")
            
            if matches:
                results.append({
                    **repo,
                    "matches": matches
                })
        
        results.sort(key=lambda x: len(x['matches']), reverse=True)
        return results[:limit]
        
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


def get_repo_readme(repo_name: str) -> dict:
    """
    Get the README content of a repository from the main branch.
    
    Args:
        repo_name: Name of the repository.
        
    Returns:
        Dict with README content and metadata.
    """
    try:
        g = _get_github()
        repo = g.get_user(USER).get_repo(repo_name)
        readme = repo.get_readme()
        
        return {
            "repo": repo_name,
            "branch": repo.default_branch,
            "filename": readme.name,
            "content": readme.decoded_content.decode('utf-8'),
            "url": readme.html_url
        }
        
    except Exception as e:
        return {"error": f"Failed to get README: {str(e)}"}


def get_file_content(repo_name: str, file_path: str) -> dict:
    """
    Get the content of a specific file from the main branch of a repository.
    
    Args:
        repo_name: Name of the repository.
        file_path: Path to the file in the repo (e.g., 'src/main.py').
        
    Returns:
        Dict with file content and metadata.
    """
    try:
        g = _get_github()
        repo = g.get_user(USER).get_repo(repo_name)
        
        # Get file from the default (main) branch
        file_content = repo.get_contents(file_path, ref=repo.default_branch)
        
        return {
            "repo": repo_name,
            "branch": repo.default_branch,
            "file_path": file_path,
            "filename": file_content.name,
            "content": file_content.decoded_content.decode('utf-8'),
            "size": file_content.size,
            "url": file_content.html_url
        }
        
    except Exception as e:
        return {"error": f"Failed to get file content: {str(e)}"}


def search_and_read_repo(keywords: list[str]) -> dict:
    """
    Search for the best matching repository and read its README from the main branch.
    Combines search_repos and get_repo_readme for convenience.
    
    Args:
        keywords: List of keywords to search for the repository.
        
    Returns:
        Dict with repo info and README content, or error.
    """
    try:
        # Search for the best matching repo
        matches = search_repos(keywords, limit=1)
        
        if not matches:
            return {"error": f"No repositories found matching: {keywords}"}
        
        if 'error' in matches[0]:
            return matches[0]
        
        best_match = matches[0]
        repo_name = best_match['name']
        
        # Get the README from the main branch
        readme_result = get_repo_readme(repo_name)
        
        if 'error' in readme_result:
            return {
                "repo": best_match,
                "readme": None,
                "note": f"Found repo but couldn't read README: {readme_result['error']}"
            }
        
        return {
            "repo": {
                "name": best_match['name'],
                "description": best_match['description'],
                "url": best_match['url'],
                "matches": best_match['matches']
            },
            "readme": readme_result['content']
        }
        
    except Exception as e:
        return {"error": f"Search and read failed: {str(e)}"}


# --- TESTING ---
if __name__ == "__main__":
    print("🐙 Testing GitHub Tools...")
    
    # Test 1: List repos
    print("\n--- List Repos ---")
    repos = list_my_repos(limit=3)
    for r in repos:
        if 'error' not in r:
            print(f"  • {r['name']} ({r['language']}) ⭐{r['stars']}")
        else:
            print(f"  Error: {r['error']}")
    
    # Test 2: Search and read
    print("\n--- Search and Read ---")
    result = search_and_read_repo(["virtual"])
    if 'error' not in result:
        print(f"  Found: {result['repo']['name']}")
        print(f"  README preview: {result['readme'][:200] if result['readme'] else 'No README'}...")
    else:
        print(f"  Error: {result['error']}")
