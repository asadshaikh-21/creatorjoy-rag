from yt_dlp import YoutubeDL

def fetch_instagram_info(url: str):
    """
    Extract basic metadata from Instagram reel
    """
    ydl_opts = {
        "quiet": True,
        "noplaylist": True
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        "title": info.get("title", "Instagram Reel"),
        "duration": info.get("duration"),
        "url": url,
        "platform": "instagram"
    }