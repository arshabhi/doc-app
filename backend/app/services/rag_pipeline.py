# app/services/rag_pipeline.py

import os
import logging
import asyncio
from typing import List, Tuple, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

from app.core.config import settings
from app.db.models import Document as DocumentModel

logger = logging.getLogger(__name__)


# -----------------------------
# RAG Pipeline Main Entry
# -----------------------------
async def run_rag_pipeline(
    user_message: str,
    user_id: str,
    db: AsyncSession,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Retrieval-Augmented Generation pipeline for a user's message.
    Retrieves the user's documents, builds embeddings (or loads index),
    and uses an LLM to generate a contextualized answer.
    """

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
        # We assume meta_data may store structured info like {"text": "..."}
        content = doc.meta_data.get("text") if doc.meta_data else None
        if not content:
            continue

        for chunk in splitter.split_text(content):
            texts.append(chunk)
            metadatas.append({"filename": doc.filename, "owner_id": str(user_id)})

    if not texts:
        return ("No valid text found in your uploaded documents.", [])

    # Step 3: Create vector store in-memory
    embeddings = OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
    )
    vector_store = await asyncio.to_thread(FAISS.from_texts, texts, embeddings, metadatas=metadatas)

    # Step 4: Retrieve & generate response
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    llm = ChatOpenAI(
        temperature=0.3,
        model_name="gpt-4o-mini",
        openai_api_key=settings.OPENAI_API_KEY,
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )

    logger.info(f"Running RAG pipeline for user {user_id}: {user_message[:60]}...")

    # Run the blocking LLM inference off the event loop
    result = await asyncio.to_thread(qa_chain, {"query": user_message})

    llm_output = result["result"]
    sources = [
        {
            "filename": doc.metadata.get("filename", ""),
            "excerpt": doc.page_content[:200],
        }
        for doc in result["source_documents"]
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
