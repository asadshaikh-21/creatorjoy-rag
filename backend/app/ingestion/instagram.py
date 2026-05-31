import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")

client = ApifyClient(APIFY_TOKEN)


def fetch_instagram_info(url: str):
    """
    Fetch Instagram reel metadata using Apify
    """

    run_input = {
        "directUrls": [url],
        "resultsLimit": 1,
        "resultsType": "details"
    }

    run = client.actor("apify/instagram-scraper").call(
        run_input=run_input
    )

    dataset_id = run.default_dataset_id

    items = list(
        client.dataset(dataset_id).iterate_items()
    )

    if not items:
        raise Exception("No Instagram data returned")

    item = items[0]

    return {
        "video_id": item.get("id", ""),
        "title": item.get("caption", "")[:120],
        "caption": item.get("caption", ""),
        "creator": item.get("ownerUsername", "Unknown"),
        "creator_name": item.get("ownerFullName", ""),
        "views": item.get("videoViewCount", 0),
        "plays": item.get("videoPlayCount", 0),
        "likes": item.get("likesCount", 0),
        "comments": item.get("commentsCount", 0),
        "duration": item.get("videoDuration", 0),
        "hashtags": item.get("hashtags", []),
        "timestamp": item.get("timestamp"),
        "url": url,
        "platform": "instagram",

        "top_comments": [
            c.get("text", "")
            for c in item.get("latestComments", [])[:20]
            if c.get("text")
        ]
    }