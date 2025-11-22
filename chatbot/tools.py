from langchain_core.tools import tool
from curl_cffi import requests
from newspaper import Article

MEDIUM_ARTICLES = {
    "LLMs in Practice": "https://medium.com/@pamudu1111/llms-in-practice-how-i-choose-the-right-model-f87a49f2b861",
    "Automated Election Vote Counting": "https://medium.com/@pamudu1111/automated-election-vote-counting-7b89900f7333",
    "Guess The Country": "https://medium.com/@pamudu1111/guess-the-country-4b983ff36616"
}

YOUTUBE_VIDEOS = {
    "Hybrid Transformers for Music Source Separation": "https://www.youtube.com/watch?v=OWMBehI2mLY&t=683s",
    "Hierarchical Attention Networks for Document Classification": "https://www.youtube.com/watch?v=JfgFRSjEucE&t=3s",
    "Fashion Trend Analyzer": "https://www.youtube.com/watch?v=obiv7TysnTQ"
}

@tool
def get_medium_article(topic: str) -> str:
    """
    Retrieves the content of a Medium article based on the topic.
    Available topics:
    - "LLMs in Practice"
    - "Automated Election Vote Counting"
    - "Guess The Country"
    """
    # Fuzzy matching
    url = None
    for key, link in MEDIUM_ARTICLES.items():
        if topic.lower() in key.lower():
            url = link
            break
    
    if not url:
        return f"Article not found for topic: {topic}. Available topics: {list(MEDIUM_ARTICLES.keys())}"

    try:
        # This bypasses the TLS Fingerprint check
        response = requests.get(url, impersonate="chrome")

        if response.status_code == 200:
            article = Article(url)
            article.download_state = 2 # Skip download, we already have the HTML
            article.set_html(response.text)
            article.parse()
            
            return f"Title: {article.title}\n\n{article.text}"
        else:
            return f"Failed to fetch article. Status code: {response.status_code}"

    except Exception as e:
        return f"Error fetching article: {e}"

@tool
def get_youtube_video_info(topic: str) -> str:
    """
    Retrieves the YouTube video link based on the topic.
    Available topics:
    - "Hybrid Transformers for Music Source Separation"
    - "Hierarchical Attention Networks for Document Classification"
    - "Fashion Trend Analyzer"
    """
    url = None
    for key, link in YOUTUBE_VIDEOS.items():
        if topic.lower() in key.lower():
            url = link
            break
            
    if not url:
        return f"Video not found for topic: {topic}. Available topics: {list(YOUTUBE_VIDEOS.keys())}"
    
    return f"Here is the video for '{topic}': {url}"
