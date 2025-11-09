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
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.utils.qdrant import search_vectors

logger = logging.getLogger(__name__)

# -----------------------------
# RAG Pipeline Main Entry
# -----------------------------
async def run_rag_pipeline(
    user_message: str,
    document_id: str,
    user_id: str,
    db: AsyncSession,
    llm=None,  # Optional injection (default: Gemini)
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Qdrant-powered Retrieval-Augmented Generation (RAG) pipeline.
    - Uses HuggingFace embeddings for retrieval
    - Uses Gemini for response generation
    """

    # ✅ Step 1: Fetch user's documents
    docs = await _get_user_documents(db, user_id, document_id)
    if not docs:
        return ("No documents found for your account. Please upload a document first.", [])

    logger.info(f"📄 Retrieved {len(docs)} documents for user {user_id}")

    # ✅ Step 2: Prepare embedding model
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # ✅ Step 3: Embed the user query asynchronously
    query_vector = await asyncio.to_thread(embedding_model.embed_query, user_message)

    # ✅ Step 4: Retrieve context chunks from Qdrant (filtered by owner_id)
    qdrant_results = search_vectors(
        query_vector=query_vector,
        filters={"owner_id": str(user_id), "document_id": str(document_id)},
        limit=5,
        mmr=True,
    )
    if not qdrant_results:
        return ("No relevant information found in your uploaded documents.", [])

    logger.info(f"🔍 Retrieved {len(qdrant_results)} context chunks from Qdrant")

    # ✅ Step 5: Construct context text
    context_text = "\n\n".join(
        [res["payload"].get("text", "") for res in qdrant_results if res.get("payload")]
    )

    # ✅ Step 6: Initialize Gemini if not provided
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise RuntimeError("❌ GEMINI_API_KEY not found in environment variables.")

    llm = llm or ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.2,
    )

    # ✅ Step 7: Create prompt
    prompt = ChatPromptTemplate.from_template("""
You are an intelligent assistant helping summarize and reason over user documents.

Answer the user's question based only on the following context:

{context}

Question: {question}

If the answer cannot be derived from the context, clearly say so.
""")

    # ✅ Step 8: Build LangChain RAG flow
    rag_chain = (
        {"context": lambda _: context_text, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    logger.info(f"🤖 Running RAG inference for user {user_id}...")

    # ✅ Step 9: Run inference safely in a background thread
    llm_output = await asyncio.to_thread(rag_chain.invoke, user_message)

    # ✅ Step 10: Prepare response sources
    sources = [
        {
            "filename": res["payload"].get("filename", ""),
            "excerpt": res["payload"].get("text", "")[:200],
            "score": res["score"],
        }
        for res in qdrant_results
    ]

    logger.info("✅ RAG pipeline completed successfully.")
    return llm_output, sources


# -----------------------------
# Helper: Load user documents
# -----------------------------
async def _get_user_documents(db: AsyncSession, user_id: str, document_id: str) -> List[DocumentModel]:
    """Retrieve all documents belonging to a user."""
    stmt = select(DocumentModel).where(DocumentModel.owner_id == user_id).where(DocumentModel.id == document_id)
    result = await db.execute(stmt)
    return result.scalars().all()