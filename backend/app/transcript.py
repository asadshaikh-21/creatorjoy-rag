import os
import re
import json
import subprocess
from typing import Dict, Any, List
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi
from app.ingestion.instagram import fetch_instagram_info
from app.ingestion.audio_extractor import extract_audio
from app.ingestion.whisper import transcribe_audio
from youtube_transcript_api import YouTubeTranscriptApi


# -----------------------------
# YOUTUBE ID EXTRACTOR
# -----------------------------
def extract_youtube_id(url: str) -> str:
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)",
        r"youtube\.com/shorts/([^&\n?#]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError("Invalid YouTube URL")


# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


# -----------------------------
# SMART CHUNKING (RAG OPTIMIZED)
# -----------------------------
def smart_chunk(text: str, max_words: int = 80) -> List[str]:
    words = text.split()

    chunks = [
        " ".join(words[i:i + max_words])
        for i in range(0, len(words), max_words)
    ]

    return [clean_text(c) for c in chunks if c.strip()]


# -----------------------------
# TRANSCRIPT FETCH (ROBUST)
# -----------------------------
from youtube_transcript_api import YouTubeTranscriptApi

def safe_transcript_fetch(video_id: str):
    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id)
        return [
            {
                "text": snippet.text,
                "start": float(snippet.start),
                "duration": float(getattr(snippet, "duration", 0) or 0),
                "end": float(snippet.start) + float(getattr(snippet, "duration", 0) or 0),
            }
            for snippet in fetched
        ]
    except Exception as e:
        print(f"[TRANSCRIPT ERROR] {e}")
        return []


# -----------------------------
# YOUTUBE TRANSCRIPT MAIN
# -----------------------------
def get_youtube_transcript(url: str) -> Dict[str, Any]:

    video_id = extract_youtube_id(url)

    metadata = {
        "video_id": video_id,
        "title": "Unknown",
        "creator": "Unknown",
        "platform": "youtube",
        "views": 0,
        "likes": 0,
        "comments": 0,
        "duration": 0,
        "upload_date": "Unknown",
        "follower_count": 0,
        "url": url
    }

    # -------------------------
    # yt-dlp metadata (optional but useful)
    # -------------------------
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", url],
            capture_output=True,
            text=True,
            timeout=20
        )

        if result.returncode == 0 and result.stdout:
            info = json.loads(result.stdout)

            metadata.update({
                "title": info.get("title", "Unknown"),
                "creator": info.get("uploader", "Unknown"),
                "views": info.get("view_count", 0),
                "likes": info.get("like_count", 0),
                "comments": info.get("comment_count", 0),
                "duration": info.get("duration", 0),
                "upload_date": info.get("upload_date", "Unknown"),
                "follower_count": (
                    info.get("channel_follower_count")
                    or info.get("subscriber_count")
                    or info.get("channel_subscriber_count")
                    or 0
                ),
            })

    except Exception as e:
        print(f"[METADATA WARN] {e}")

    # -------------------------
    # TRANSCRIPT FETCH
    # -------------------------
    raw = safe_transcript_fetch(video_id)

    hook_text = " ".join(
        clean_text(item.get("text", ""))
        for item in raw
        if isinstance(item, dict) and item.get("start", 9999) <= 5
    ).strip()

    texts = []

    for item in raw:
        if isinstance(item, dict):
            text = item.get("text", "")
        else:
            text = getattr(item, "text", "")

        if text and text.strip():
            texts.append(clean_text(text))

    # -------------------------
    # WHISPER FALLBACK
    # -------------------------
    if not texts:
        print(f"[WARN] No transcript found for {video_id}")
        print("[INFO] Falling back to Whisper transcription...")

        audio_path = None

        try:
            audio_path = extract_audio(url)

            whisper_text = transcribe_audio(audio_path)

            if whisper_text and whisper_text.strip():
                texts = [clean_text(whisper_text)]
                print("[SUCCESS] Whisper transcription completed")

        except Exception as e:
            print(f"[WHISPER FALLBACK ERROR] {e}")

        finally:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)

    # -------------------------
    # LAST RESORT FALLBACK
    # -------------------------
    if not texts:
        fallback = f"""
        Title: {metadata['title']}
        Creator: {metadata['creator']}
        Views: {metadata['views']}
        Likes: {metadata['likes']}
        Description: This video discusses core ideas from the creator.
        """.strip()

        texts = [fallback]

    full_text = " ".join(texts)

    chunks = smart_chunk(full_text, max_words=80)

    return {
        "success": True,
        "transcript": full_text,
        "chunks": chunks,
        "timestamps": list(range(len(chunks))),
        "hook_preview": hook_text,
        "metadata": metadata,
        "label": ""
    }


# -----------------------------
# INSTAGRAM FALLBACK
# -----------------------------
def get_instagram_transcript(url: str):

    metadata = fetch_instagram_info(url)

    audio_path = None
    transcript = ""

    try:
        audio_path = extract_audio(url)
        transcript = transcribe_audio(audio_path)
    except Exception as e:
        print(f"[INSTAGRAM AUDIO WARN] {e}")
        transcript = ""
    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

    extra_context = f"""
Caption:
{metadata.get('caption', '')}

Hashtags:
{' '.join(metadata.get('hashtags', []))}

Comments:
{' '.join(metadata.get('top_comments', []))}
"""

    full_content = transcript + "\n\n" + extra_context

    chunks = smart_chunk(full_content, max_words=80)
    hook_text = chunks[0] if chunks else ""

    return {
        "success": True,
        "transcript": full_content,
        "chunks": chunks,
        "timestamps": list(range(len(chunks))),
        "hook_preview": hook_text,
        "metadata": {
            "video_id": metadata.get("video_id"),
            "title": metadata.get("title"),
            "creator": metadata.get("creator"),
            "follower_count": metadata.get("follower_count", 0),
            "platform": "instagram",
            "source": "instagram",
            "thumbnail": (
                metadata.get("thumbnail")
                or metadata.get("displayUrl")
                or metadata.get("thumbnailUrl")
                or metadata.get("thumbnailSrc")
                or metadata.get("imageUrl")
                or metadata.get("coverUrl")
                or ""
            ),
            "views": metadata.get("views", 0),
            "plays": metadata.get("plays", 0),
            "likes": metadata.get("likes", 0),
            "comments": metadata.get("comments", 0),
            "duration": metadata.get("duration", 0),

            "hashtags": metadata.get("hashtags", []),
            "caption": metadata.get("caption", ""),

            "url": url,
        },
        "label": ""
    }


# -----------------------------
# UNIFIED ENTRY POINT
# -----------------------------
def get_video_data(url: str, video_label: str):

    url_lower = url.lower()

    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        data = get_youtube_transcript(url)

    elif "instagram.com" in url_lower:
        data = get_instagram_transcript(url)

    else:
        raise ValueError(f"Unsupported URL: {url}")

    meta = data["metadata"]

    views = max(meta.get("views", 1), 1)
    likes = meta.get("likes", 0)
    comments = meta.get("comments", 0)

    meta["engagement_rate"] = round(((likes + comments) / views) * 100, 2)

    data["label"] = video_label

    return data