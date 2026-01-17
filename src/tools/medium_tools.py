"""
Medium Tools - Fetch articles and content from Medium RSS feed.
"""

import feedparser
import json
import warnings
from curl_cffi import requests

# Suppress SyntaxWarning from newspaper3k (invalid escape sequences in Python 3.12+)
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    from newspaper import Article

# --- CONFIGURATION ---
USERNAME = "pamudu1111"
RSS_URL = f"https://medium.com/feed/@{USERNAME}"


def list_medium_articles(limit: int = 5) -> list[dict]:
    """
    Fetches metadata for the latest Medium articles.
    
    Args:
        limit: Maximum number of articles to return.
        
    Returns:
        List of article metadata dicts with title, date, link, and preview.
    """
    try:
        feed = feedparser.parse(RSS_URL)
        
        if not feed.entries:
            return []
        
        articles = []
        for entry in feed.entries[:limit]:
            # Get a preview from summary (strip HTML)
            preview = entry.get('summary', '')[:200] if entry.get('summary') else ''
            
            articles.append({
                "title": entry.title,
                "date": entry.published,
                "link": entry.link,
                "preview": preview
            })
        
        return articles
        
    except Exception as e:
        return [{"error": f"Failed to fetch articles: {str(e)}"}]


def get_medium_article_content(article_link: str) -> dict:
    """
    Fetches the full content of a specific Medium article.
    
    Args:
        article_link: The URL of the Medium article.
        
    Returns:
        Dict with title, content, and metadata.
    """
    try:
        # Use curl_cffi to bypass TLS fingerprint checks
        response = requests.get(article_link, impersonate="chrome")
        
        if response.status_code != 200:
            return {"error": f"Failed to fetch article. Status: {response.status_code}"}
        
        # Parse with newspaper
        article = Article(article_link)
        article.download_state = 2  # Skip download, we have HTML
        article.set_html(response.text)
        article.parse()
        
        return {
            "title": article.title,
            "content": article.text,
            "authors": article.authors,
            "publish_date": str(article.publish_date) if article.publish_date else None,
            "link": article_link
        }
        
    except Exception as e:
        return {"error": f"Failed to parse article: {str(e)}"}


def search_medium_articles(keywords: list[str], limit: int = 5) -> list[dict]:
    """
    Search Medium articles by keywords in title/content.
    
    Args:
        keywords: List of keywords to search for.
        limit: Maximum results to return.
        
    Returns:
        List of matching articles with relevance info.
    """
    try:
        feed = feedparser.parse(RSS_URL)
        
        if not feed.entries:
            return []
        
        results = []
        keywords_lower = [k.lower() for k in keywords]
        
        for entry in feed.entries:
            title_lower = entry.title.lower()
            summary_lower = entry.get('summary', '').lower()
            
            # Check for keyword matches
            matches = []
            for kw in keywords_lower:
                if kw in title_lower:
                    matches.append(f"title:{kw}")
                if kw in summary_lower:
                    matches.append(f"content:{kw}")
            
            if matches:
                results.append({
                    "title": entry.title,
                    "date": entry.published,
                    "link": entry.link,
                    "matches": matches,
                    "preview": entry.get('summary', '')[:200]
                })
        
        # Sort by number of matches
        results.sort(key=lambda x: len(x['matches']), reverse=True)
        
        return results[:limit]
        
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


# --- TESTING ---
if __name__ == "__main__":
    print("📰 Testing Medium Tools...")
    
    # Test 1: List articles
    print("\n--- List Articles ---")
    articles = list_medium_articles(limit=3)
    for a in articles:
        print(f"  • {a.get('title', 'N/A')}")
    
    # Test 2: Search articles
    print("\n--- Search for 'AI' ---")
    results = search_medium_articles(["AI", "agent"], limit=2)
    for r in results:
        print(f"  • {r.get('title')} (matches: {r.get('matches')})")
    
    # Test 3: Get full content (if articles exist)
    if articles and 'link' in articles[0]:
        print("\n--- Get Full Content ---")
        content = get_medium_article_content(articles[0]['link'])
        print(f"  Title: {content.get('title')}")
        print(f"  Length: {len(content.get('content', ''))} chars")
