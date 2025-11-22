import os
import json
import requests
import feedparser
import cloudscraper
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("medium-mcp-server")

# Medium API Base URL
BASE_URL = "https://api.medium.com/v1"

def get_headers():
    token = os.getenv("MEDIUM_ACCESS_TOKEN")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Charset": "utf-8"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

@mcp.tool()
def get_latest_articles_rss(username: str) -> str:
    """
    Get the latest articles for a user using their public RSS feed.
    Does NOT require an API token.
    
    Args:
        username: The Medium username (without the @).
    """
    rss_url = f"https://medium.com/feed/@{username}"
    
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(rss_url)
        
        if response.status_code == 404:
            return "No articles found (User might not have public stories or username is incorrect)."
        elif response.status_code in [403, 503]:
            return f"Access denied by Medium (Status {response.status_code}). Bot protection might be active."
        elif response.status_code != 200:
            return f"Error fetching feed: Status {response.status_code}"
            
        feed = feedparser.parse(response.text)
        
        if feed.bozo:
            return f"Error parsing feed content: {feed.bozo_exception}"
            
        articles = []
        for entry in feed.entries:
            tags = entry.get('tags') or []
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "tags": [tag.term for tag in tags],
                "summary": entry.summary
            })
            
        return json.dumps(articles, indent=2)
        
    except Exception as e:
        return f"An error occurred: {str(e)}"

@mcp.tool()
def get_user_details() -> str:
    """
    Get details of the authenticated user.
    Requires MEDIUM_ACCESS_TOKEN to be set.
    """
    url = f"{BASE_URL}/me"
    try:
        headers = get_headers()
        if "Authorization" not in headers:
            return "Error: MEDIUM_ACCESS_TOKEN not found. This tool requires authentication."
            
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.RequestException as e:
        return f"Error fetching user details: {str(e)}"

@mcp.tool()
def list_publications(user_id: str) -> str:
    """
    List publications that the user is subscribed to, writes for, or edits.
    Requires MEDIUM_ACCESS_TOKEN to be set.
    
    Args:
        user_id: The unique identifier for the user.
    """
    url = f"{BASE_URL}/users/{user_id}/publications"
    try:
        headers = get_headers()
        if "Authorization" not in headers:
            return "Error: MEDIUM_ACCESS_TOKEN not found. This tool requires authentication."

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.RequestException as e:
        return f"Error fetching publications: {str(e)}"

if __name__ == "__main__":
    mcp.run()