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

## System Overview

           ┌──────────────────────────────┐
           │      Frontend (Swagger / UI) │
           └──────────────┬───────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │      FastAPI Backend         │
           │  /api/process-videos         │
           │  /api/chat                   │
           └──────────────┬───────────────┘
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ YouTube Flow │  │ Instagram Flow│  │ Embedding    │
│              │  │              │  │ Pipeline     │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       ▼                 ▼                 ▼
 yt-dlp + transcript   yt-dlp + audio   Gemini Embeddings
 API (fallback + SS)   extraction       (batchEmbedContents)
       │                 │                 │
       └──────┬──────────┴──────────┬──────┘
              ▼                     ▼
        Smart Chunking        Vector Store
        (RAG chunks)          (ChromaDB)
              │                     │
              └──────────┬──────────┘
                         ▼
                 RAG Chat System
                 (Gemini LLM)
                         │
                         ▼
              Streaming Response API

## Run Backend

```bash
cd backend
pip install -r requirements.txt
python run.py
