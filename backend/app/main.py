from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import json
import logging
from dotenv import load_dotenv
from app.services.ingestion_service import process_instagram
import requests

load_dotenv()

from .transcript import get_video_data
from .embeddings import embed_video_transcript, delete_session as delete_vector_session
from .rag import chat_with_rag, stream_chat_with_rag, clear_session
from fastapi.responses import StreamingResponse, Response

# -------------------------
# LOGGING (PRODUCTION READY)
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CreatorJoy RAG API",
    version="1.0.0"
)

def process_video(url: str):

    if "instagram.com" in url:
        return process_instagram(url)

    # fallback to YouTube
    return process_youtube(url)

# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/image-proxy")
def image_proxy(url: str):
    try:
        r = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.instagram.com/",
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            },
            timeout=15,
        )
        r.raise_for_status()

        return Response(
            content=r.content,
            media_type=r.headers.get("content-type", "image/jpeg"),
            headers={
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*",
            },
        )

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Image proxy failed: {e}")

# -------------------------
# MODELS
# -------------------------
class VideoRequest(BaseModel):
    video_a_url: str
    video_b_url: str


class ChatRequest(BaseModel):
    session_id: str
    question: str
    stream: Optional[bool] = True


# -------------------------
# MEMORY STORE (TEMPORARY)
# (later replace with Redis / DB)
# -------------------------
sessions = {}


# -------------------------
# HEALTH
# -------------------------
@app.get("/")
def root():
    return {
        "status": "running",
        "message": "CreatorJoy RAG API",
        "version": "1.0.0",
    }


@app.get("/api/health")
def health():
    return {"status": "healthy"}


# -------------------------
# PROCESS VIDEOS
# -------------------------
@app.post("/api/process-videos")
async def process_videos(request: VideoRequest):

    session_id = str(uuid.uuid4())
    logger.info(f"New session created: {session_id}")

    try:
        # ---------------- Video A ----------------
        logger.info("[1/4] Fetching Video A...")
        video_a = get_video_data(request.video_a_url, "A")
        logger.info(f"Video A: {video_a['metadata'].get('title')}")

        # ---------------- Video B ----------------
        logger.info("[2/4] Fetching Video B...")
        video_b = get_video_data(request.video_b_url, "B")
        logger.info(f"Video B: {video_b['metadata'].get('title')}")

        # ---------------- Embedding ----------------
        logger.info("[3/4] Embedding Video A...")
        chunks_a = embed_video_transcript(video_a, session_id)

        logger.info("[4/4] Embedding Video B...")
        chunks_b = embed_video_transcript(video_b, session_id)

        total = chunks_a + chunks_b
        logger.info(f"Embedding complete: {total} chunks")

        # ---------------- SESSION STORE ----------------
        sessions[session_id] = {
            "video_a": {
                "url": request.video_a_url,
                "metadata": video_a["metadata"],
                "transcript_preview": video_a.get("transcript", "")[:300],
                "chunks_count": chunks_a,
            },
            "video_b": {
                "url": request.video_b_url,
                "metadata": video_b["metadata"],
                "transcript_preview": video_b.get("transcript", "")[:300],
                "chunks_count": chunks_b,
            },
            "total_chunks": total,
        }

        return {
            "success": True,
            "session_id": session_id,
            **sessions[session_id],
            "total_chunks_embedded": total,
            "message": "Videos processed successfully",
            "suggested_questions": [
                "Why did Video A get more engagement than Video B?",
                "What's the engagement rate of each video?",
                "Compare hooks in first 5 seconds",
                "Who created each video?",
                "Suggest improvements for Video B",
            ]
        }

    except Exception as e:
        logger.error(f"process_videos failed: {str(e)}")

        # cleanup
        try:
            delete_vector_session(session_id)
            clear_session(session_id)
        except:
            pass

        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# CHAT (STREAM + NON STREAM)
# -------------------------
@app.post("/api/chat")
async def chat(request: ChatRequest):

    if request.session_id not in sessions:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please process videos first."
        )

    if request.stream:

        async def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"

                full_response = ""

                async for token in stream_chat_with_rag(
                    request.session_id,
                    request.question
                ):
                    full_response += token
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

                yield f"data: {json.dumps({'type': 'done', 'full_response': full_response})}\n\n"

            except Exception as e:
                logger.error(f"stream error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )

    result = await chat_with_rag(request.session_id, request.question)
    return {"success": True, **result}


# -------------------------
# SESSION INFO
# -------------------------
@app.get("/api/session/{session_id}")
def get_session(session_id: str):

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        **sessions[session_id]
    }


# -------------------------
# DELETE SESSION
# -------------------------
@app.delete("/api/session/{session_id}")
def delete_session_endpoint(session_id: str):

    if session_id in sessions:
        try:
            delete_vector_session(session_id)
            clear_session(session_id)
            del sessions[session_id]
        except Exception as e:
            logger.warning(f"delete session warning: {e}")

    return {
        "success": True,
        "message": "Session deleted"
    }


# -------------------------
# SUGGESTED QUESTIONS
# -------------------------
@app.get("/api/suggested-questions")
def suggested_questions():
    return {
        "questions": [
            "Why did Video A get more engagement than Video B?",
            "What's the engagement rate of each video?",
            "Compare hooks in first 5 seconds",
            "Who created Video B?",
            "Suggest improvements for Video B",
            "Which video has better structure?",
            "What topics are covered in Video A?",
        ]
    }