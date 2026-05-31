from apify_client import ApifyClient
from dotenv import load_dotenv
import os

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")


def fetch_instagram_info(url: str):
    """
    Fetch Instagram Reel metadata using Apify.
    """

    client = ApifyClient(APIFY_TOKEN)

    run_input = {
        "directUrls": [url],
        "resultsLimit": 1
    }

    run = client.actor("apify/instagram-scraper").call(
        run_input=run_input
    )

    dataset_id = run.default_dataset_id

    items = list(
        client.dataset(dataset_id).iterate_items()
    )

    if not items:
        return {
            "video_id": "instagram",
            "title": "Instagram Reel",
            "creator": "Unknown",
            "thumbnail": "",
            "views": 0,
            "plays": 0,
            "likes": 0,
            "comments": 0,
            "duration": 0,
            "hashtags": [],
            "caption": "",
        }

    item = items[0]

    return {
        "video_id": item.get("id", ""),
        "title": (item.get("caption", "")[:120] or "Instagram Reel"),
        "caption": item.get("caption", ""),
        "creator": item.get("ownerUsername", "Unknown"),

        # THUMBNAIL
        "thumbnail": item.get("displayUrl", ""),

        # STATS
        "views": item.get("videoViewCount", 0),
        "plays": item.get("videoPlayCount", 0),
        "likes": item.get("likesCount", 0),
        "comments": item.get("commentsCount", 0),

        # EXTRA
        "duration": item.get("videoDuration", 0),
        "hashtags": item.get("hashtags", []),
        "url": item.get("url", url),
    }