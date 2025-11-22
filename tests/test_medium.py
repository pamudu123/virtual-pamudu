import sys
import os
import json

# Add the project root to the python path so we can import the server
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from medium_mcp_server.medium_server import get_latest_articles_rss

def test_rss_feed():
    print("Testing RSS Feed Tool...")
    # Use a known medium user, e.g., 'ev' (Evan Williams) or the user's 'pamudu123'
    username = "pamudu123" 
    
    result = get_latest_articles_rss(username)
    
    try:
        data = json.loads(result)
        print(f"Successfully fetched {len(data)} articles.")
        if len(data) > 0:
            print("First article title:", data[0].get('title'))
            print("First article link:", data[0].get('link'))
        else:
            print("No articles found (or feed is empty).")
            
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
        print("Raw output:", result)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_rss_feed()
