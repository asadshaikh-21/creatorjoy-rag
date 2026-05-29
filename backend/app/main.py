from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

from .transcript import get_video_data
from .embeddings import embed_video_transcript, delete_session
from .rag import chat_with_rag, stream_chat_with_rag, clear_session

app = FastAPI(title="CreatorJoy RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class VideoRequest(BaseModel):
    video_a_url: str
    video_b_url: str

class ChatRequest(BaseModel):
    session_id: str
    question: str
    stream: Optional[bool] = True

# Store session data
sessions = {}

@app.get("/")
def root():
    return {
        "status": "running",
        "message": "CreatorJoy RAG API",
        "version": "1.0.0",
        "endpoints": {
            "process": "POST /api/process-videos",
            "chat": "POST /api/chat",
            "session": "GET /api/session/{session_id}",
            "health": "GET /api/health"
        }
    }

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "CreatorJoy RAG API"}

@app.post("/api/process-videos")
async def process_videos(request: VideoRequest):
    """Process two videos - get transcripts, embed into ChromaDB"""
    
    session_id = str(uuid.uuid4())
    
    try:
        print(f"Processing videos for session {session_id}")
        
        # Get Video A data
        print(f"Fetching Video A: {request.video_a_url}")
        video_a_data = get_video_data(request.video_a_url, "A")
        
        # Get Video B data  
        print(f"Fetching Video B: {request.video_b_url}")
        video_b_data = get_video_data(request.video_b_url, "B")
        
        # Embed both videos into ChromaDB
        print("Embedding transcripts...")
        chunks_a = embed_video_transcript(video_a_data, session_id)
        chunks_b = embed_video_transcript(video_b_data, session_id)
        
        # Store session info
        sessions[session_id] = {
            "video_a": {
                "url": request.video_a_url,
                "metadata": video_a_data["metadata"],
                "transcript_preview": video_a_data["transcript"][:300],
                "chunks_count": chunks_a,
            },
            "video_b": {
                "url": request.video_b_url,
                "metadata": video_b_data["metadata"],
                "transcript_preview": video_b_data["transcript"][:300],
                "chunks_count": chunks_b,
            },
            "total_chunks": chunks_a + chunks_b,
        }
        
        print(f"Session {session_id} ready! {chunks_a + chunks_b} total chunks")
        
        return {
            "success": True,
            "session_id": session_id,
            "video_a": sessions[session_id]["video_a"],
            "video_b": sessions[session_id]["video_b"],
            "total_chunks_embedded": chunks_a + chunks_b,
            "message": "Videos processed successfully! Ready to chat."
        }
        
    except Exception as e:
        # Clean up on error
        delete_session(session_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat with RAG - supports streaming"""
    
    if request.session_id not in sessions:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please process videos first."
        )
    
    if request.stream:
        # Streaming response
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
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )
    else:
        # Non-streaming response
        result = await chat_with_rag(request.session_id, request.question)
        return {"success": True, **result}

@app.get("/api/session/{session_id}")
def get_session(session_id: str):
    """Get session info"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, **sessions[session_id]}

@app.delete("/api/session/{session_id}")
def delete_session_endpoint(session_id: str):
    """Delete a session"""
    if session_id in sessions:
        delete_session(session_id)
        clear_session(session_id)
        del sessions[session_id]
    return {"success": True, "message": "Session deleted"}

@app.get("/api/suggested-questions")
def suggested_questions():
    """Get suggested questions for the chat"""
    return {
        "questions": [
            "Why did Video A get more engagement than Video B?",
            "What's the engagement rate of each video?",
            "Compare the hooks in the first 5 seconds of both videos",
            "Who's the creator of Video B and what's their follower count?",
            "Suggest improvements for Video B based on what worked in Video A",
            "What topics are covered in Video A?",
            "Which video has better audience retention based on the transcript?",
        ]
    }