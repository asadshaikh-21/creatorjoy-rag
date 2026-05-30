import os
from dotenv import load_dotenv
from typing import List, Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .embeddings import get_vector_store

load_dotenv()

# -----------------------------
# CONFIG (IMPORTANT FIX)
# -----------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Use ONLY available model from your API list
CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")

session_histories: Dict[str, List[Dict]] = {}


# -----------------------------
# LLM (PRODUCTION SAFE)
# -----------------------------
def get_llm(streaming: bool = False):
    return ChatGoogleGenerativeAI(
        model=CHAT_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=0.2,
        streaming=streaming,
    )


# -----------------------------
# CONTEXT BUILDER
# -----------------------------
def build_context(docs) -> str:
    if not docs:
        return "No relevant context found."

    parts = []
    for doc in docs:
        m = doc.metadata or {}

        parts.append(
            f"""
VIDEO: {m.get("video_label")}
TITLE: {m.get("title")}
CREATOR: {m.get("creator")}
VIEWS: {m.get("views")}
LIKES: {m.get("likes")}
COMMENTS: {m.get("comments")}
ENGAGEMENT: {m.get("engagement_rate")}

CONTENT:
{doc.page_content}
""".strip()
        )

    return "\n\n---\n\n".join(parts)


SYSTEM_PROMPT = """
You are a professional AI content analyst.

You compare Video A vs Video B using ONLY provided context.

Context:
{context}

History:
{history}

Question:
{question}

Rules:
- Never hallucinate
- Always compare A vs B when relevant
- Use numbers (views, likes, engagement_rate)
- Structure output:
  1. Summary
  2. Video A
  3. Video B
  4. Differences
  5. Insight
"""


# -----------------------------
# SAFE RETRIEVAL
# -----------------------------
def safe_retrieve(retriever, query: str, k: int = 6):
    try:
        docs = retriever.invoke(query)
        return docs[:k] if docs else []
    except Exception:
        return []


# -----------------------------
# CHAT (NON STREAM)
# -----------------------------
async def chat_with_rag(session_id: str, question: str):

    store = get_vector_store(session_id)
    retriever = store.as_retriever(search_kwargs={"k": 8})

    docs = safe_retrieve(retriever, question)

    context = build_context(docs)

    history = session_histories.get(session_id, [])
    history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in history[-6:]
    )

    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
    llm = get_llm(streaming=False)

    chain = prompt | llm | StrOutputParser()

    response = await chain.ainvoke({
        "context": context,
        "history": history_text,
        "question": question
    })

    session_histories.setdefault(session_id, [])
    session_histories[session_id].append({"role": "user", "content": question})
    session_histories[session_id].append({"role": "assistant", "content": response})

    return {
        "answer": response,
        "sources": [
            {
                "video": d.metadata.get("video_label"),
                "title": d.metadata.get("title"),
                "chunk": d.page_content[:150]
            }
            for d in docs[:3]
        ]
    }


# -----------------------------
# STREAM CHAT
# -----------------------------
async def stream_chat_with_rag(session_id: str, question: str):

    store = get_vector_store(session_id)
    retriever = store.as_retriever(search_kwargs={"k": 8})

    docs = safe_retrieve(retriever, question)

    context = build_context(docs)

    history = session_histories.get(session_id, [])
    history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in history[-6:]
    )

    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
    llm = get_llm(streaming=True)

    chain = prompt | llm

    full = ""

    async for chunk in chain.astream({
        "context": context,
        "history": history_text,
        "question": question
    }):
        token = chunk.content if hasattr(chunk, "content") else str(chunk)
        full += token
        yield token

    session_histories.setdefault(session_id, [])
    session_histories[session_id].append({"role": "user", "content": question})
    session_histories[session_id].append({"role": "assistant", "content": full})


# -----------------------------
# CLEAR SESSION
# -----------------------------
def clear_session(session_id: str):
    session_histories.pop(session_id, None)