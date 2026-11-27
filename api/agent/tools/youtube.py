"""YouTube tools: Pamudu's channel videos and their transcripts."""

import feedparser
from langchain_core.tools import tool
from youtube_transcript_api import YouTubeTranscriptApi

CHANNEL_ID = "UCvLnrajdjeV3w-WuBiBmX7w"
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
MAX_TRANSCRIPT_CHARS = 20_000


def _summary(entry) -> dict:
    video_id = entry.get("yt_videoid", "")
    return {
        "title": entry.get("title", ""),
        "video_id": video_id,
        "url": entry.get("link", ""),
        "published": entry.get("published", ""),
        "description": entry.get("summary", "")[:300],
        "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else "",
    }


def _entries():
    return feedparser.parse(RSS_URL).entries


@tool
def list_youtube_videos(limit: int = 5) -> dict:
    """List the latest videos on Pamudu's YouTube channel.

    Args:
        limit: How many videos to return (1-15).
    """
    try:
        return {"videos": [_summary(e) for e in _entries()[: max(1, min(limit, 15))]]}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Could not fetch YouTube videos: {exc}"}


@tool
def search_youtube_videos(keywords: list[str], limit: int = 5) -> dict:
    """Search Pamudu's YouTube videos by keywords in the title or description.

    Args:
        keywords: Words to look for.
        limit: Maximum number of matches to return.
    """
    try:
        wanted = [k.lower() for k in keywords if k.strip()]
        scored = []
        for entry in _entries():
            video = _summary(entry)
            haystack = f"{video['title']} {video['description']}".lower()
            score = sum(1 for k in wanted if k in haystack)
            if score:
                scored.append((score, video))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return {"videos": [v for _, v in scored[:limit]]}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"YouTube search failed: {exc}"}


@tool
def get_video_transcript(video_id: str) -> dict:
    """Get the transcript of one of Pamudu's YouTube videos.

    Args:
        video_id: The YouTube video id, as returned by the list or search tools.
    """
    try:
        transcript = YouTubeTranscriptApi().fetch(video_id)
        text = " ".join(snippet.text for snippet in transcript)
        return {
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "transcript": text[:MAX_TRANSCRIPT_CHARS],
        }
    except Exception as exc:  # noqa: BLE001
        return {"video_id": video_id, "error": f"No transcript available: {exc}"}
