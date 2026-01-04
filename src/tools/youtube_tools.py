"""
YouTube Tools - Fetch videos and transcripts from YouTube channel.
"""

import feedparser
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# --- CONFIGURATION ---
CHANNEL_ID = "UCvLnrajdjeV3w-WuBiBmX7w"  # @pamudu123ranasinghe7
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"


def list_youtube_videos(limit: int = 5) -> list[dict]:
    """
    Fetches metadata for the latest YouTube videos.
    
    Args:
        limit: Maximum number of videos to return.
        
    Returns:
        List of video metadata with title, video_id, link, and description.
    """
    try:
        feed = feedparser.parse(RSS_URL)
        
        if not feed.entries:
            return []
        
        videos = []
        for entry in feed.entries[:limit]:
            videos.append({
                "title": entry.title,
                "video_id": entry.yt_videoid,
                "link": entry.link,
                "published": entry.published,
                "description": entry.get('summary', '')[:300]
            })
        
        return videos
        
    except Exception as e:
        return [{"error": f"Failed to fetch videos: {str(e)}"}]


def get_video_transcript(video_id: str) -> dict:
    """
    Fetches the transcript/captions of a YouTube video.
    
    Args:
        video_id: The YouTube video ID (e.g., 'dQw4w9WgXcQ').
        
    Returns:
        Dict with video_id, transcript text, and metadata.
    """
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)
        
        formatter = TextFormatter()
        text = formatter.format_transcript(transcript)
        
        return {
            "video_id": video_id,
            "transcript": text,
            "length": len(text),
            "segments": len(transcript)
        }
        
    except Exception as e:
        return {
            "video_id": video_id,
            "error": f"Failed to fetch transcript: {str(e)}",
            "note": "Video may not have captions available."
        }


def get_latest_video_with_transcript() -> dict:
    """
    Convenience function to get the latest video with its transcript.
    
    Returns:
        Dict with video metadata and full transcript.
    """
    videos = list_youtube_videos(limit=1)
    
    if not videos or 'error' in videos[0]:
        return {"error": "No videos found"}
    
    video = videos[0]
    transcript_data = get_video_transcript(video['video_id'])
    
    return {
        "title": video['title'],
        "video_id": video['video_id'],
        "link": video['link'],
        "published": video['published'],
        "description": video['description'],
        "transcript": transcript_data.get('transcript', ''),
        "transcript_error": transcript_data.get('error')
    }


def search_video_transcripts(keywords: list[str], limit: int = 3) -> list[dict]:
    """
    Search through video transcripts for keywords.
    
    Args:
        keywords: List of keywords to search for.
        limit: Maximum videos to search through.
        
    Returns:
        List of videos with matching transcript snippets.
    """
    try:
        videos = list_youtube_videos(limit=limit)
        results = []
        keywords_lower = [k.lower() for k in keywords]
        
        for video in videos:
            if 'error' in video:
                continue
                
            transcript_data = get_video_transcript(video['video_id'])
            
            if 'error' in transcript_data:
                continue
            
            transcript_lower = transcript_data['transcript'].lower()
            
            # Find matching keywords
            matches = []
            snippets = []
            
            for kw in keywords_lower:
                if kw in transcript_lower:
                    matches.append(kw)
                    # Extract snippet around the keyword
                    idx = transcript_lower.find(kw)
                    start = max(0, idx - 100)
                    end = min(len(transcript_data['transcript']), idx + 100)
                    snippet = transcript_data['transcript'][start:end]
                    snippets.append(f"...{snippet}...")
            
            if matches:
                results.append({
                    "title": video['title'],
                    "video_id": video['video_id'],
                    "link": video['link'],
                    "matches": matches,
                    "snippets": snippets[:2]  # Limit snippets
                })
        
        return results
        
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


# --- TESTING ---
if __name__ == "__main__":
    print("🎬 Testing YouTube Tools...")
    
    # Test 1: List videos
    print("\n--- List Videos ---")
    videos = list_youtube_videos(limit=3)
    for v in videos:
        print(f"  • {v.get('title', 'N/A')} ({v.get('video_id', 'N/A')})")
    
    # Test 2: Get transcript (if videos exist)
    if videos and 'video_id' in videos[0]:
        print(f"\n--- Get Transcript for: {videos[0]['title']} ---")
        transcript = get_video_transcript(videos[0]['video_id'])
        if 'transcript' in transcript:
            print(f"  Length: {transcript['length']} chars")
            print(f"  Preview: {transcript['transcript'][:200]}...")
        else:
            print(f"  Error: {transcript.get('error')}")
