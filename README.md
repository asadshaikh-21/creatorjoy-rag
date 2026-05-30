# CreatorJoy RAG Chatbot

AI-powered RAG chatbot for comparing creator videos using transcript embeddings and vector search.

## What this project does

This project takes two social media video URLs (YouTube / Instagram), extracts transcripts + metadata, stores embeddings in a vector database, and allows users to chat with the content using a RAG pipeline.

The goal is to help creators understand why one video performed better than another.

---

## Features

- YouTube + Instagram video processing
- Transcript extraction
- Metadata analysis
- Engagement rate calculation
- ChromaDB vector storage
- LangChain-based RAG chatbot
- Gemini-powered responses
- Session memory support

---

## Tech Stack

### Backend
- FastAPI
- LangChain
- ChromaDB
- Gemini API
- Python

### Frontend (planned)
- Next.js
- TailwindCSS

---

## Current Progress

- Backend APIs setup
- Vector embedding pipeline integrated
- Gemini integration completed
- Basic transcript extraction working
- Frontend not started yet

---

## 🧠 System Architecture

```mermaid
flowchart TD

    A[Frontend (Swagger / UI)] --> B[FastAPI Backend]

    B --> C[YouTube Pipeline]
    B --> D[Instagram Pipeline]
    B --> E[Embedding Pipeline]

    C --> C1[yt-dlp + YouTube Transcript API]
    D --> D1[yt-dlp + Whisper Audio Transcription]

    C1 --> F[Smart Chunking]
    D1 --> F

    F --> G[Gemini Embeddings API]

    G --> H[ChromaDB Vector Store]

    H --> I[RAG Chat System (Gemini LLM)]

    I --> J[Streaming Response API]

## Run Backend

```bash
cd backend
pip install -r requirements.txt
python run.py
