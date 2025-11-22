from unittest import result
from mcp.server import Server
from mcp.types import Tool, TextContent
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize server
app = Server("youtube-api-server")

# YouTube API setup
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY) if YOUTUBE_API_KEY else None


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/shorts\/([^&\n?#]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return url


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    tools = [
        Tool(
            name="get_transcript",
            description="Get the transcript/subtitles from a YouTube video",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_url": {"type": "string", "description": "YouTube video URL or ID"},
                    "language": {"type": "string", "description": "Language code", "default": "en"}
                },
                "required": ["video_url"]
            }
        )
    ]
    
    if youtube:
        tools.extend([
            Tool(
                name="search_videos",
                description="Search for YouTube videos",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "max_results": {"type": "integer", "description": "Max results", "default": 10}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_video_details",
                description="Get detailed information about a YouTube video",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "video_url": {"type": "string", "description": "YouTube video URL or ID"}
                    },
                    "required": ["video_url"]
                }
            ),
            Tool(
                name="get_channel_info",
                description="Get information about a YouTube channel",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "channel_id": {"type": "string", "description": "YouTube channel ID"}
                    },
                    "required": ["channel_id"]
                }
            )
        ])
    
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "get_transcript":
            video_id = extract_video_id(arguments["video_url"])
            language = arguments.get("language", "en")
            
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            full_transcript = "\n".join([entry['text'] for entry in transcript_list])
            
            return [TextContent(type="text", text=f"Transcript:\n\n{full_transcript}")]
        
        elif name == "search_videos" and youtube:
            query = arguments["query"]
            max_results = arguments.get("max_results", 10)
            
            request = youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results
            )
            response = request.execute()
            
            results = []
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                channel = item['snippet']['channelTitle']
                description = item['snippet']['description']
                
                results.append(
                    f"Title: {title}\n"
                    f"Channel: {channel}\n"
                    f"URL: https://youtube.com/watch?v={video_id}\n"
                    f"Description: {description[:200]}...\n"
                )
            
            return [TextContent(type="text", text="\n---\n".join(results))]
        
        elif name == "get_video_details" and youtube:
            video_id = extract_video_id(arguments["video_url"])
            
            request = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                return [TextContent(type="text", text="Video not found")]
            
            item = response['items'][0]
            snippet = item['snippet']
            stats = item['statistics']
            
            details = (
                f"Title: {snippet['title']}\n"
                f"Channel: {snippet['channelTitle']}\n"
                f"Published: {snippet['publishedAt']}\n"
                f"Views: {stats.get('viewCount', 'N/A')}\n"
                f"Likes: {stats.get('likeCount', 'N/A')}\n"
                f"Comments: {stats.get('commentCount', 'N/A')}\n"
                f"Description: {snippet['description']}"
            )
            
            return [TextContent(type="text", text=details)]
        
        elif name == "get_channel_info" and youtube:
            channel_id = arguments["channel_id"]
            
            request = youtube.channels().list(
                part="snippet,statistics,contentDetails",
                id=channel_id
            )
            response = request.execute()
            
            if not response['items']:
                return [TextContent(type="text", text="Channel not found")]
            
            item = response['items'][0]
            snippet = item['snippet']
            stats = item['statistics']
            
            info = (
                f"Channel: {snippet['title']}\n"
                f"Subscribers: {stats.get('subscriberCount', 'Hidden')}\n"
                f"Total Views: {stats.get('viewCount', 'N/A')}\n"
                f"Videos: {stats.get('videoCount', 'N/A')}\n"
                f"Description: {snippet['description']}"
            )
            
            return [TextContent(type="text", text=info)]
        
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    # async def main():
    #     async with stdio_server() as (read_stream, write_stream):
    #         await app.run(
    #             read_stream,
    #             write_stream,
    #             app.create_initialization_options()
    #         )
    
    # asyncio.run(main())
    result = asyncio.run(call_tool("get_video_details", {"video_url": "https://www.youtube.com/watch?v=OWMBehI2mLY&t=683s"}))
    print(result)