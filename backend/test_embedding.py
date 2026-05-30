# test_embedding.py

import uuid

from app.transcript import get_video_data
from app.embeddings import embed_video_transcript

session_id = str(uuid.uuid4())

video = get_video_data(
    "https://www.instagram.com/reel/DJKEFtHRk5X/",
    "A"
)

count = embed_video_transcript(
    video,
    session_id
)

print("Embedded Chunks:", count)
print("Session:", session_id)