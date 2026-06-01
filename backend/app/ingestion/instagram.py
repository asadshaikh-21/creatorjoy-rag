import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")

client = ApifyClient(APIFY_TOKEN)
profile_followers_cache = {}

def fetch_instagram_profile_followers(username: str) -> int:
    if not username or username == "Unknown":
        return 0

    if username in profile_followers_cache:
        return profile_followers_cache[username]

    try:
        run_input = {
            "usernames": [username],
            "resultsLimit": 1
        }

        run = client.actor("apify/instagram-profile-scraper").call(
            run_input=run_input
        )

        items = list(
            client.dataset(run.default_dataset_id).iterate_items()
        )

        if not items:
            profile_followers_cache[username] = 0
            return 0

        profile = items[0]
        print("PROFILE KEYS:", profile.keys())
        print("PROFILE ITEM:", profile)

        count = (
            profile.get("followersCount")
            or profile.get("followers_count")
            or profile.get("followers")
            or profile.get("numberOfFollowers")
            or profile.get("edge_followed_by", {}).get("count")
            or profile.get("ownerFollowersCount")
            or 0
        )

        profile_followers_cache[username] = count
        return count

    except Exception as e:
        print(f"[INSTAGRAM PROFILE FOLLOWERS WARN] {e}")
        profile_followers_cache[username] = 0
        return 0

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
    creator = item.get("ownerUsername", "Unknown")
    follower_count = fetch_instagram_profile_followers(creator)

    return {
        "video_id": item.get("id", ""),
        "title": item.get("caption", "")[:120],
        "caption": item.get("caption", ""),
        "creator": creator,
        "creator_name": item.get("ownerFullName", ""),
        "follower_count": follower_count,
        "thumbnail": (
            item.get("displayUrl")
            or item.get("thumbnailUrl")
            or item.get("thumbnailSrc")
            or item.get("imageUrl")
            or item.get("coverUrl")
            or ""
        ),
        "displayUrl": item.get("displayUrl", ""),
        "videoUrl": item.get("videoUrl", ""),
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