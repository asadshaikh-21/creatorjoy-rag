# CreatorJoy

AI-powered creator analytics platform that uses Retrieval-Augmented Generation (RAG) to analyze YouTube videos and Instagram Reels through natural language conversations.

CreatorJoy extracts transcripts, metadata, engagement metrics, hashtags, creator information, and audience signals, then combines semantic search with Gemini-powered reasoning to generate actionable content insights.

---

## Features

* YouTube video ingestion
* Instagram Reel ingestion
* Automatic transcript extraction
* Whisper fallback for videos without captions
* Metadata and engagement analysis
* Creator profile insights
* Semantic chunking
* Gemini embeddings
* ChromaDB vector storage
* Retrieval-Augmented Generation (RAG)
* Streaming AI responses
* Session-based chat memory

---

## Tech Stack

| Layer              | Technology                        |
| ------------------ | --------------------------------- |
| Frontend           | Next.js, TypeScript, Tailwind CSS |
| Backend            | FastAPI, Python                   |
| LLM                | Gemini 2.5 Flash                  |
| Embeddings         | Gemini Embeddings                 |
| Vector Database    | ChromaDB                          |
| Speech-to-Text     | Faster Whisper                    |
| Video Processing   | yt-dlp                            |
| Instagram Metadata | Apify                             |
| RAG Framework      | LangChain                         |

---

## System Architecture

```mermaid
flowchart LR

    U[User] --> F[Frontend]

    F --> API[FastAPI Backend]

    API --> YT[YouTube]
    API --> IG[Instagram]

    YT --> YTM[Metadata Extraction]
    YT --> YTT[Transcript API]

    IG --> IGM[Apify Scraper]
    IG --> IGA[Audio Extraction]

    IGA --> WH[Whisper]

    YTM --> PROC[Content Processing]
    YTT --> PROC

    IGM --> PROC
    WH --> PROC

    PROC --> CHUNK[Smart Chunking]

    CHUNK --> EMBED[Gemini Embeddings]

    EMBED --> DB[ChromaDB]

    DB --> RAG[RAG Retrieval]

    RAG --> LLM[Gemini LLM]

    LLM --> RESP[Streaming Response]

    RESP --> F
```

## Processing Workflow

1. User submits a YouTube video or Instagram Reel URL.
2. Metadata such as title, creator, views, likes, comments, hashtags, and duration is extracted.
3. Transcript content is collected:

   * YouTube Transcript API for captioned videos.
   * Whisper fallback for videos without captions.
4. Content is cleaned and divided into semantic chunks.
5. Gemini Embeddings converts chunks into vector representations.
6. ChromaDB stores embeddings for semantic retrieval.
7. Relevant chunks are retrieved through the RAG pipeline.
8. Gemini generates context-aware responses grounded in video content.
9. Responses are streamed back to the user.

---

## Cost-Efficient Architecture

CreatorJoy is designed to minimize AI inference costs while maintaining response quality.

* Gemini Embeddings for low-cost vector generation
* ChromaDB self-hosted vector storage
* Whisper invoked only when captions are unavailable
* Semantic retrieval reduces LLM context size
* Streaming responses improve user experience

This architecture keeps processing costs low while enabling scalable creator analytics.

---

## Running the Backend

```bash
cd backend

pip install -r requirements.txt

python run.py
```

---

## API Documentation

After starting the server:

```text
http://localhost:8000/docs
```

Swagger UI can be used to test all API endpoints.

---

## Roadmap

* Multi-video creator comparison
* Hook and retention analysis
* Thumbnail effectiveness analysis
* Audience sentiment analysis
* Trend detection across creator content
* Creator growth recommendations
* Production deployment

---

## Author

Asad Shaikh

Information Technology Student | Full-Stack Developer | AI Engineer

* LinkedIn
* GitHub
* Portfolio
