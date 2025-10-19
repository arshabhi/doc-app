# app/services/rag_pipeline.py

import os
import logging
import asyncio
from typing import List, Tuple, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.db.models import Document as DocumentModel

logger = logging.getLogger(__name__)

# -----------------------------
# RAG Pipeline Main Entry
# -----------------------------
async def run_rag_pipeline(
    user_message: str,
    user_id: str,
    db: AsyncSession,
    llm=None,  # Optional injection from API (defaults to Gemini)
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Retrieval-Augmented Generation pipeline for a user's message.
    Uses Gemini (via LangChain) for embeddings + LLM response.
    """

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not found in environment variables.")

    # Step 1: Fetch user's documents
    docs = await _get_user_documents(db, user_id)
    if not docs:
        return (
            "No documents found for your account. Please upload a document first.",
            [],
        )

    # Step 2: Prepare text chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts, metadatas = [], []

    for doc in docs:
        content = doc.meta_data.get("text") if doc.meta_data else None
        if not content:
            continue

        for chunk in splitter.split_text(content):
            texts.append(chunk)
            metadatas.append({"filename": doc.filename, "owner_id": str(user_id)})

    if not texts:
        return ("No valid text found in your uploaded documents.", [])

    logger.info("Text chunks prepared for RAG pipeline.")

    # Step 3: Create embeddings + vector store
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", 
        google_api_key=GEMINI_API_KEY
    )
    vector_store = await asyncio.to_thread(
        FAISS.from_texts, 
        texts, 
        embeddings, 
        metadatas=metadatas
    )
    
    # Step 4: Set up retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    # Step 5: Use Gemini model (inject or default)
    llm = llm or ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=GEMINI_API_KEY,
        temperature=0.2,
    )

    # Step 6: Create RAG prompt template
    prompt = ChatPromptTemplate.from_template("""
Answer the question based only on the following context:

{context}

Question: {question}

Provide a detailed answer based on the context above. If the answer cannot be found in the context, say so.
""")

    # Step 7: Format documents helper function
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Step 8: Create RAG chain using LCEL
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    logger.info(f"Running Gemini RAG pipeline for user {user_id}: {user_message[:60]}...")

    # Step 9: Get retrieved documents for sources
    retrieved_docs = await asyncio.to_thread(
        retriever.get_relevant_documents, 
        user_message
    )

    # Step 10: Run LLM inference safely in background thread
    llm_output = await asyncio.to_thread(rag_chain.invoke, user_message)

    # Step 11: Parse sources
    sources = [
        {
            "filename": doc.metadata.get("filename", ""),
            "excerpt": doc.page_content[:200],
        }
        for doc in retrieved_docs
    ]

    return llm_output, sources


# -----------------------------
# Helper: Load user documents
# -----------------------------
async def _get_user_documents(db: AsyncSession, user_id: str) -> List[DocumentModel]:
    """Retrieve all documents for the given user."""
    stmt = select(DocumentModel).where(DocumentModel.owner_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()