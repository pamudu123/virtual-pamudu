"""GitHub tools: browse Pamudu's public repositories."""

import os
from functools import lru_cache

from github import Auth, Github
from langchain_core.tools import tool

GITHUB_USER = "pamudu123"
MAX_FILE_CHARS = 20_000


@lru_cache(maxsize=1)
def _client() -> Github:
    token = os.getenv("GITHUB_TOKEN")
    return Github(auth=Auth.Token(token)) if token else Github()


def _repo_summary(repo) -> dict:
    return {
        "name": repo.name,
        "description": repo.description or "",
        "language": repo.language or "",
        "stars": repo.stargazers_count,
        "updated": repo.updated_at.date().isoformat() if repo.updated_at else "",
        "url": repo.html_url,
    }


def _all_repos(limit: int) -> list[dict]:
    repos = _client().get_user(GITHUB_USER).get_repos(sort="updated")
    return [_repo_summary(r) for r in repos[:limit]]


@tool
def list_github_repos(limit: int = 6) -> dict:
    """List Pamudu's most recently updated public GitHub repositories.

    Args:
        limit: How many repositories to return (1-20).
    """
    try:
        return {"repos": _all_repos(max(1, min(limit, 20)))}
    except Exception as exc:  # noqa: BLE001 - surfaced to the model
        return {"error": f"Could not list repositories: {exc}"}


@tool
def search_github_repos(keywords: list[str], limit: int = 5) -> dict:
    """Search Pamudu's GitHub repositories by keywords in the name or description.

    Args:
        keywords: Words to look for, e.g. ["chess", "vision"].
        limit: Maximum number of matches to return.
    """
    try:
        wanted = [k.lower() for k in keywords if k.strip()]
        scored = []
        for repo in _all_repos(100):
            haystack = f"{repo['name']} {repo['description']}".lower()
            score = sum(1 for k in wanted if k in haystack)
            if score:
                scored.append((score, repo))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return {"repos": [repo for _, repo in scored[:limit]]}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Repository search failed: {exc}"}


@tool
def get_repo_readme(repo_name: str) -> dict:
    """Read the README of one of Pamudu's repositories.

    Args:
        repo_name: Exact repository name, as returned by the list or search tools.
    """
    try:
        repo = _client().get_user(GITHUB_USER).get_repo(repo_name)
        readme = repo.get_readme()
        return {
            "repo": repo_name,
            "url": readme.html_url,
            "content": readme.decoded_content.decode("utf-8", "replace")[:MAX_FILE_CHARS],
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Could not read README of {repo_name}: {exc}"}


@tool
def get_repo_file(repo_name: str, file_path: str) -> dict:
    """Read one file, or list one directory, on the default branch of one of Pamudu's repositories.

    Args:
        repo_name: Exact repository name.
        file_path: Path inside the repository, e.g. "src/main.py". Use "" for the root listing.
    """
    try:
        repo = _client().get_user(GITHUB_USER).get_repo(repo_name)
        item = repo.get_contents(file_path, ref=repo.default_branch)
        if isinstance(item, list):
            return {"repo": repo_name, "path": file_path, "entries": [i.path for i in item]}
        return {
            "repo": repo_name,
            "path": file_path,
            "url": item.html_url,
            "content": item.decoded_content.decode("utf-8", "replace")[:MAX_FILE_CHARS],
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Could not read {file_path} in {repo_name}: {exc}"}
