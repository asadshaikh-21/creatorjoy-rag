def route_video(url: str) -> str:
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"

    if "instagram.com" in url:
        return "instagram"

    return "unsupported"