from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from .embeddings import get_vector_store
import os
from dotenv import load_dotenv

load_dotenv()

# Store memory per session
session_memories = {}
session_histories = {}

def get_llm(streaming=False):
    """Get Gemini LLM"""
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
        streaming=streaming,
    )

SYSTEM_PROMPT = """You are an expert content analyst AI for CreatorJoy, helping creators understand their video performance.

You have access to transcripts and metadata for Video A and Video B.

When answering:
1. Always cite which video (Video A or Video B) your information comes from
2. Use specific data points (engagement rates, views, likes, comments)
3. Be specific about timestamps or content sections when relevant
4. Give actionable, creator-focused insights
5. Compare videos objectively using data

Context from videos:
{context}

Chat History:
{chat_history}

Question: {question}

Answer with specific citations (e.g., "In Video A..." or "Video B's transcript shows..."):"""

def get_rag_chain(session_id: str):
    """Build RAG chain for a session"""
    
    vector_store = get_vector_store(session_id)
    retriever = vector_store.as_retriever(
        search_type="mmr",  # Maximum Marginal Relevance for diverse results
        search_kwargs={
            "k": 6,
            "fetch_k": 12,
        }
    )
    
    if session_id not in session_memories:
        session_memories[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
    
    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=SYSTEM_PROMPT
    )
    
    chain = ConversationalRetrievalChain.from_llm(
        llm=get_llm(),
        retriever=retriever,
        memory=session_memories[session_id],
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True,
        verbose=False,
    )
    
    return chain

async def chat_with_rag(session_id: str, question: str):
    """Chat with RAG and return response with sources"""
    
    chain = get_rag_chain(session_id)
    
    result = chain.invoke({"question": question})
    
    answer = result.get("answer", "")
    source_docs = result.get("source_documents", [])
    
    # Format sources
    sources = []
    seen = set()
    for doc in source_docs:
        meta = doc.metadata
        source_key = f"{meta.get('video_id')}_{meta.get('chunk_index')}"
        if source_key not in seen:
            seen.add(source_key)
            sources.append({
                "video": meta.get("video_label", "Unknown"),
                "platform": meta.get("platform", "unknown"),
                "creator": meta.get("creator", "Unknown"),
                "chunk": doc.page_content[:150] + "...",
            })
    
    # Store history
    if session_id not in session_histories:
        session_histories[session_id] = []
    session_histories[session_id].append({
        "role": "user",
        "content": question
    })
    session_histories[session_id].append({
        "role": "assistant", 
        "content": answer,
        "sources": sources
    })
    
    return {
        "answer": answer,
        "sources": sources,
        "history": session_histories[session_id]
    }

async def stream_chat_with_rag(session_id: str, question: str):
    """Stream chat response token by token"""
    
    vector_store = get_vector_store(session_id)
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 6}
    )
    
    # Get relevant docs
    docs = retriever.get_relevant_documents(question)
    
    context = "\n\n".join([
        f"[Video {doc.metadata.get('video_id', '?')}] {doc.page_content}"
        for doc in docs
    ])
    
    # Get history
    history = ""
    if session_id in session_histories:
        for msg in session_histories[session_id][-6:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history += f"{role}: {msg['content']}\n"
    
    # Build prompt
    full_prompt = SYSTEM_PROMPT.format(
        context=context,
        chat_history=history,
        question=question
    )
    
    llm = get_llm(streaming=True)
    
    full_response = ""
    async for chunk in llm.astream(full_prompt):
        token = chunk.content
        full_response += token
        yield token
    
    # Save to history
    sources = []
    for doc in docs[:3]:
        sources.append({
            "video": f"Video {doc.metadata.get('video_id', '?')}",
            "platform": doc.metadata.get("platform", "unknown"),
            "creator": doc.metadata.get("creator", "Unknown"),
            "chunk": doc.page_content[:150] + "...",
        })
    
    if session_id not in session_histories:
        session_histories[session_id] = []
    session_histories[session_id].append({
        "role": "user", "content": question
    })
    session_histories[session_id].append({
        "role": "assistant",
        "content": full_response,
        "sources": sources
    })

def clear_session(session_id: str):
    """Clear session memory"""
    if session_id in session_memories:
        del session_memories[session_id]
    if session_id in session_histories:
        del session_histories[session_id]