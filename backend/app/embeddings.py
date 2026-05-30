import os
import time
import logging
from typing import List

from dotenv import load_dotenv
from google import genai
from langchain_core.documents import Document
from langchain_chroma import Chroma

load_dotenv()

logger = logging.getLogger(__name__)

# --------------------------
# CONFIG
# --------------------------
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chromadb")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY missing")

client = genai.Client(api_key=GEMINI_API_KEY)


# --------------------------
# EMBEDDING (SAFE + BATCHED)
# --------------------------
def embed_batch(texts: List[str], retries: int = 3):
    """
    Single API call batch embedding (FAST + CHEAP)
    """
    texts = [t for t in texts if t and t.strip()]

    if not texts:
        return []

    for attempt in range(retries):
        try:
            response = client.models.embed_content(
                model="models/gemini-embedding-2",
                contents=texts
            )
            return [e.values for e in response.embeddings]

        except Exception as e:
            logger.warning(f"[EMBED RETRY {attempt+1}] {e}")
            time.sleep(1.5 * (attempt + 1))

    logger.error("[EMBED FAILED] returning zero vectors")
    return [[] for _ in texts]


# --------------------------
# EMBEDDING WRAPPER (LANGCHAIN)
# --------------------------
class GeminiEmbeddingWrapper:
    def embed_documents(self, texts: List[str]):
        vectors = embed_batch(texts)
        return vectors

    def embed_query(self, text: str):
        vecs = embed_batch([text])
        return vecs[0] if vecs else []


# --------------------------
# VECTOR STORE
# --------------------------
def get_vector_store(session_id: str):
    return Chroma(
        collection_name=f"session_{session_id}",
        embedding_function=GeminiEmbeddingWrapper(),
        persist_directory=CHROMA_PATH
    )


# --------------------------
# CLEANING
# --------------------------
def clean_chunks(chunks):
    return [
        c.strip()
        for c in chunks
        if isinstance(c, str) and c.strip() and len(c.strip()) > 10
    ]


# --------------------------
# MAIN PIPELINE
# --------------------------
def embed_video_transcript(video_data: dict, session_id: str) -> int:

    label = video_data.get("label", "unknown")
    metadata = video_data.get("metadata") or {}

    chunks = video_data.get("chunks", [])

    # fallback
    if not chunks:
        transcript = video_data.get("transcript", "")
        chunks = [transcript] if transcript else []

    chunks = clean_chunks(chunks)

    if not chunks:
        logger.warning(f"No chunks → skipping {label}")
        return 0

    # IMPORTANT: pre-check embeddings before storing
    vectors = embed_batch(chunks)

    documents = []

    for i, chunk in enumerate(chunks):
        documents.append(
            Document(
                page_content=chunk,
                metadata={
                    "video_id": metadata.get("video_id", label),
                    "video_label": f"Video {label}",
                    "title": metadata.get("title", "Unknown"),
                    "creator": metadata.get("creator", "Unknown"),
                    "views": metadata.get("views", 0),
                    "likes": metadata.get("likes", 0),
                    "comments": metadata.get("comments", 0),
                    "engagement_rate": metadata.get("engagement_rate", 0),
                    "chunk_index": i,
                    "session_id": session_id,
                }
            )
        )

    try:
        store = get_vector_store(session_id)

        store.add_documents(documents)

        # ensure persistence
        try:
            store.persist()
        except Exception:
            pass

        logger.info(f"[OK] Embedded {len(documents)} chunks for {label}")
        return len(documents)

    except Exception as e:
        logger.error(f"[EMBED ERROR] {e}")
        return 0


# --------------------------
# SESSION CLEANUP
# --------------------------
def delete_session(session_id: str):
    try:
        import shutil

        path = os.path.join(CHROMA_PATH, f"session_{session_id}")

        if os.path.exists(path):
            shutil.rmtree(path)
            logger.info(f"[CLEANED] session {session_id}")

    except Exception as e:
        logger.warning(f"delete_session failed: {e}")