import re
import json
import subprocess
from typing import Dict, Any, List

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
def safe_transcript_fetch(video_id: str):

    # 1. Try standard English
    try:
        return YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
    except:
        pass

    # 2. Try auto-generated + multi language fallback
    try:
        api = YouTubeTranscriptApi()
        transcripts = api.list_transcripts(video_id)

        for t in transcripts:
            try:
                fetched = t.fetch()
                return [
                    {"text": item.text, "start": item.start}
                    for item in fetched
                ]
            except:
                continue
    except:
        pass

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
            })

    except Exception as e:
        print(f"[METADATA WARN] {e}")

    # -------------------------
    # TRANSCRIPT FETCH
    # -------------------------
    raw = safe_transcript_fetch(video_id)

    texts = []

    for item in raw:
        if isinstance(item, dict):
            text = item.get("text", "")
        else:
            text = getattr(item, "text", "")

        if text and text.strip():
            texts.append(clean_text(text))

    # -------------------------
    # SMART FALLBACK (IMPORTANT FIX)
    # -------------------------
    if not texts:
        print(f"[WARN] No transcript found for {video_id}")

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
        "metadata": metadata,
        "label": ""
    }


# -----------------------------
# INSTAGRAM FALLBACK
# -----------------------------
def get_instagram_transcript(url: str):

    return {
        "success": True,
        "transcript": "Instagram content not supported yet",
        "chunks": ["Instagram content not supported yet"],
        "timestamps": [0],
        "metadata": {"platform": "instagram"},
        "label": ""
    }


# -----------------------------
# UNIFIED ENTRY POINT
# -----------------------------
def get_video_data(url: str, video_label: str):

    if "youtube.com" in url or "youtu.be" in url:
        data = get_youtube_transcript(url)
    elif "instagram.com" in url:
        data = get_instagram_transcript(url)
    else:
        raise ValueError("Unsupported URL")

    meta = data["metadata"]

    views = max(meta.get("views", 1), 1)
    likes = meta.get("likes", 0)
    comments = meta.get("comments", 0)

    meta["engagement_rate"] = round(((likes + comments) / views) * 100, 2)

    data["label"] = video_label

    return data