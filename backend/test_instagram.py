# test_instagram.py

from app.transcript import get_video_data
from app.embeddings import embed_video_transcript
import uuid

url = "https://www.instagram.com/reel/DJKEFtHRk5X/"
session_id = str(uuid.uuid4())

print("Fetching Instagram data...")

data = get_video_data(url, "IG_TEST")

print("Chunks:", len(data["chunks"]))
print("Transcript length:", len(data["transcript"]))

print("\nEmbedding...")

count = embed_video_transcript(data, session_id)

print("\nEmbedded chunks:", count)
print("Session:", session_id)