from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chromadb")

def get_embeddings():
    """Get Google Gemini embeddings"""
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

def get_vector_store(session_id: str):
    """Get ChromaDB vector store for a session"""
    embeddings = get_embeddings()
    return Chroma(
        collection_name=f"session_{session_id}",
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )

def embed_video_transcript(video_data: dict, session_id: str) -> int:
    """Chunk and embed video transcript into ChromaDB"""
    
    transcript = video_data["transcript"]
    label = video_data["label"]
    metadata = video_data["metadata"]
    
    # Smart chunking - 500 chars with 50 overlap
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = splitter.split_text(transcript)
    
    # Create documents with rich metadata
    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk,
            metadata={
                "video_id": label,
                "video_label": f"Video {label}",
                "platform": metadata.get("platform", "unknown"),
                "creator": metadata.get("creator", "Unknown"),
                "title": metadata.get("title", "Unknown"),
                "views": metadata.get("views", 0),
                "likes": metadata.get("likes", 0),
                "comments": metadata.get("comments", 0),
                "engagement_rate": metadata.get("engagement_rate", 0),
                "chunk_index": i,
                "session_id": session_id,
            }
        )
        documents.append(doc)
    
    # Store in ChromaDB
    vector_store = get_vector_store(session_id)
    vector_store.add_documents(documents)
    
    return len(documents)

def delete_session(session_id: str):
    """Delete ChromaDB collection for a session"""
    try:
        vector_store = get_vector_store(session_id)
        vector_store.delete_collection()
    except:
        pass