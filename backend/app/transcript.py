from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re
import httpx
import os

def extract_youtube_id(url: str) -> str:
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/shorts\/([^&\n?#]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract YouTube ID from URL: {url}")

def get_youtube_transcript(url: str) -> dict:
    """Get transcript and metadata for YouTube video"""
    try:
        video_id = extract_youtube_id(url)
        
        # Get transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        transcript_text = formatter.format_transcript(transcript_list)
        
        # Get metadata via YouTube oEmbed API (free, no API key needed)
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        
        metadata = {
            "video_id": video_id,
            "url": url,
            "platform": "youtube",
            "title": "Unknown",
            "creator": "Unknown",
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        }
        
        try:
            async def fetch_metadata():
                async with httpx.AsyncClient() as client:
                    resp = await client.get(oembed_url, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        metadata["title"] = data.get("title", "Unknown")
                        metadata["creator"] = data.get("author_name", "Unknown")
            
            import asyncio
            asyncio.get_event_loop().run_until_complete(fetch_metadata())
        except:
            pass
        
        # Get stats via noembed
        try:
            noembed_url = f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}"
            import urllib.request
            import json
            with urllib.request.urlopen(noembed_url, timeout=5) as response:
                data = json.loads(response.read())
                metadata["title"] = data.get("title", metadata["title"])
                metadata["creator"] = data.get("author_name", metadata["creator"])
        except:
            pass

        return {
            "transcript": transcript_text,
            "metadata": metadata,
            "chunks": [item["text"] for item in transcript_list],
            "timestamps": [item["start"] for item in transcript_list],
        }
        
    except Exception as e:
        raise Exception(f"YouTube transcript error: {str(e)}")


def get_instagram_transcript(url: str) -> dict:
    """Get transcript for Instagram Reel using yt-dlp"""
    try:
        import yt_dlp
        import tempfile
        import os
        
        # Extract info without downloading
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        metadata = {
            "url": url,
            "platform": "instagram",
            "title": "Instagram Reel",
            "creator": "Unknown",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "duration": 0,
            "follower_count": "N/A",
            "hashtags": [],
            "upload_date": "Unknown",
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    metadata["title"] = info.get("title", "Instagram Reel")
                    metadata["creator"] = info.get("uploader", "Unknown")
                    metadata["views"] = info.get("view_count", 0) or 0
                    metadata["likes"] = info.get("like_count", 0) or 0
                    metadata["comments"] = info.get("comment_count", 0) or 0
                    metadata["duration"] = info.get("duration", 0) or 0
                    metadata["upload_date"] = info.get("upload_date", "Unknown")
                    
                    # Extract hashtags from description
                    description = info.get("description", "")
                    hashtags = re.findall(r'#\w+', description)
                    metadata["hashtags"] = hashtags[:10]
                    
                    # Get thumbnail
                    thumbnails = info.get("thumbnails", [])
                    if thumbnails:
                        metadata["thumbnail"] = thumbnails[-1].get("url", "")
        except Exception as e:
            print(f"yt-dlp metadata error: {e}")
        
        # For Instagram, transcript is approximated from description/title
        # Real transcription would need Whisper API
        transcript_text = f"Instagram Reel by {metadata['creator']}: {metadata['title']}"
        
        # Try to get audio transcript using yt-dlp + description
        description_text = f"Video: {metadata['title']}\nCreator: {metadata['creator']}\nHashtags: {' '.join(metadata['hashtags'])}"
        
        return {
            "transcript": description_text,
            "metadata": metadata,
            "chunks": [description_text],
            "timestamps": [0],
        }
        
    except Exception as e:
        raise Exception(f"Instagram transcript error: {str(e)}")


def get_video_data(url: str, video_label: str) -> dict:
    """Main function to get video data based on URL"""
    if "youtube.com" in url or "youtu.be" in url:
        data = get_youtube_transcript(url)
    elif "instagram.com" in url:
        data = get_instagram_transcript(url)
    else:
        raise ValueError(f"Unsupported URL: {url}")
    
    data["label"] = video_label  # "A" or "B"
    
    # Calculate engagement rate
    metadata = data["metadata"]
    views = metadata.get("views", 0) or 1
    likes = metadata.get("likes", 0) or 0
    comments = metadata.get("comments", 0) or 0
    metadata["engagement_rate"] = round(((likes + comments) / views) * 100, 2)
    
    return data