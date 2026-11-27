"""Medium tools: Pamudu's blog articles, read from the public RSS feed."""

import feedparser
from bs4 import BeautifulSoup
from langchain_core.tools import tool

MEDIUM_USERNAME = "pamudu1111"
RSS_URL = f"https://medium.com/feed/@{MEDIUM_USERNAME}"
MAX_ARTICLE_CHARS = 20_000


def _entry_html(entry) -> str:
    content = entry.get("content")
    if content:
        return content[0].get("value", "")
    return entry.get("summary", "")


def _entry_text(entry) -> str:
    return BeautifulSoup(_entry_html(entry), "html.parser").get_text(" ", strip=True)


def _entry_image(entry) -> str:
    img = BeautifulSoup(_entry_html(entry), "html.parser").find("img")
    return img.get("src", "") if img else ""


def _clean_url(url: str) -> str:
    return url.split("?")[0].rstrip("/")


def _summary(entry) -> dict:
    return {
        "title": entry.get("title", ""),
        "date": entry.get("published", ""),
        "url": _clean_url(entry.get("link", "")),
        "preview": _entry_text(entry)[:220],
        "image": _entry_image(entry),
        "tags": [t.get("term", "") for t in entry.get("tags", [])][:4],
    }


def _entries():
    return feedparser.parse(RSS_URL).entries


@tool
def list_medium_articles(limit: int = 5) -> dict:
    """List Pamudu's latest Medium articles.

    Args:
        limit: How many articles to return (1-10).
    """
    try:
        return {"articles": [_summary(e) for e in _entries()[: max(1, min(limit, 10))]]}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Could not fetch Medium articles: {exc}"}


@tool
def search_medium_articles(keywords: list[str], limit: int = 5) -> dict:
    """Search Pamudu's Medium articles by keywords in the title or body.

    Args:
        keywords: Words to look for, e.g. ["RAG", "agents"].
        limit: Maximum number of matches to return.
    """
    try:
        wanted = [k.lower() for k in keywords if k.strip()]
        scored = []
        for entry in _entries():
            title = entry.get("title", "").lower()
            body = _entry_text(entry).lower()
            score = sum(3 for k in wanted if k in title) + sum(1 for k in wanted if k in body)
            if score:
                scored.append((score, _summary(entry)))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return {"articles": [a for _, a in scored[:limit]]}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Medium search failed: {exc}"}


@tool
def read_medium_article(url: str) -> dict:
    """Read the full text of one of Pamudu's Medium articles.

    Args:
        url: The article URL, as returned by the list or search tools.
    """
    try:
        target = _clean_url(url)
        for entry in _entries():
            if _clean_url(entry.get("link", "")) == target:
                return {
                    "title": entry.get("title", ""),
                    "url": target,
                    "date": entry.get("published", ""),
                    "content": _entry_text(entry)[:MAX_ARTICLE_CHARS],
                }
        return {"error": "That article is not in Pamudu's Medium feed."}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Could not read the article: {exc}"}
