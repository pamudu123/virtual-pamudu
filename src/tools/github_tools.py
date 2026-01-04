"""
GitHub Tools - Fetch repository info, PRs, and activity from GitHub.
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


def get_repo_status(repo_name: str) -> dict:
    """
    Get status of a GitHub repository (like 'git status' for remote).
    
    Args:
        repo_name: Name of the repository.
        
    Returns:
        Dict with branch info, last commit, PR/issue counts, stars.
    """
    try:
        g = _get_github()
        repo = g.get_user(USER).get_repo(repo_name)
        branch = repo.get_branch(repo.default_branch)
        commit = branch.commit
        
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "default_branch": repo.default_branch,
            "last_commit": {
                "sha": commit.sha[:7],
                "message": commit.commit.message,
                "date": str(commit.commit.author.date)
            },
            "open_prs": repo.get_pulls(state='open').totalCount,
            "open_issues": repo.get_issues(state='open').totalCount,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "url": repo.html_url
        }
        
    except Exception as e:
        return {"error": f"Failed to get repo status: {str(e)}"}


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


def list_my_prs(state: str = "open", limit: int = 10) -> list[dict]:
    """
    List Pull Requests created by the user.
    
    Args:
        state: 'open', 'closed', or 'all'.
        limit: Maximum PRs to return.
        
    Returns:
        List of PR metadata.
    """
    try:
        g = _get_github()
        query = f"author:{USER} type:pr state:{state}"
        prs = g.search_issues(query=query)
        
        result = []
        for pr in prs[:limit]:
            result.append({
                "number": pr.number,
                "title": pr.title,
                "repo": pr.repository.name if pr.repository else "unknown",
                "state": pr.state,
                "created": str(pr.created_at),
                "url": pr.html_url
            })
        
        return result
        
    except Exception as e:
        return [{"error": f"Failed to list PRs: {str(e)}"}]


def check_review_requests() -> list[dict]:
    """
    Check for PRs where the user's review has been requested.
    
    Returns:
        List of PRs awaiting review.
    """
    try:
        g = _get_github()
        query = f"review-requested:{USER} state:open type:pr"
        prs = g.search_issues(query=query)
        
        if prs.totalCount == 0:
            return []
        
        result = []
        for pr in prs:
            result.append({
                "number": pr.number,
                "title": pr.title,
                "repo": pr.repository.name if pr.repository else "unknown",
                "url": pr.html_url
            })
        
        return result
        
    except Exception as e:
        return [{"error": f"Failed to check reviews: {str(e)}"}]


def get_repo_readme(repo_name: str) -> dict:
    """
    Get the README content of a repository.
    
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
            "filename": readme.name,
            "content": readme.decoded_content.decode('utf-8'),
            "url": readme.html_url
        }
        
    except Exception as e:
        return {"error": f"Failed to get README: {str(e)}"}


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
    
    # Test 2: Get repo status (if repos exist)
    if repos and 'error' not in repos[0]:
        print(f"\n--- Repo Status: {repos[0]['name']} ---")
        status = get_repo_status(repos[0]['name'])
        if 'error' not in status:
            print(f"  Branch: {status['default_branch']}")
            print(f"  Last commit: {status['last_commit']['message'][:50]}")
            print(f"  Open PRs: {status['open_prs']}")
        else:
            print(f"  Error: {status['error']}")
    
    # Test 3: List PRs
    print("\n--- My Open PRs ---")
    prs = list_my_prs(state="open", limit=3)
    for pr in prs:
        if 'error' not in pr:
            print(f"  • #{pr['number']} {pr['title']} ({pr['repo']})")
        else:
            print(f"  Error: {pr['error']}")
