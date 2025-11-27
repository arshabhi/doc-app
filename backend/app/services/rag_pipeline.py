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
from app.core.config import settings

from pydantic import BaseModel, Field
from typing import List, Optional

class Citation(BaseModel):
    context_id: int = Field(..., description="Context index referenced by the LLM")


class RAGResponse(BaseModel):
    answer: str
    citations: List[Citation] = []


async def run_rag_pipeline(
    user_message: str,
    document_id: str,
    user_id: str,
    db: AsyncSession,
    llm=None,
) -> Tuple[str, List[Dict[str, Any]]]:

    # -----------------------------
    # 1️⃣ Fetch documents
    # -----------------------------
    docs = await _get_user_documents(db, user_id, document_id)
    if not docs:
        return ("No documents found.", [])

    # -----------------------------
    # 2️⃣ Embeddings
    # -----------------------------
    embedding_model = HuggingFaceEmbeddings(model_name=settings.HUGGINGFACE_EMBEDDING_MODEL)
    query_vector = await asyncio.to_thread(embedding_model.embed_query, user_message)

    # -----------------------------
    # 3️⃣ Vector retrieval (Qdrant)
    # -----------------------------
    qdrant_results = await search_vectors(
        query_vector=query_vector,
        filters={"owner_id": str(user_id), "document_id": str(document_id)},
        limit=5,
        mmr=True,
    )

    if not qdrant_results:
        return ("No relevant information found.", [])

    # -----------------------------
    # 4️⃣ Create numbered context blocks
    # -----------------------------
    indexed_results = []
    context_blocks = []

    for idx, res in enumerate(qdrant_results, start=1):  # ensure 1-based indexing
        indexed_results.append({
            "index": idx,
            "filename": res["payload"].get("filename"),
            "page": res["payload"].get("page"),
            "excerpt": res["payload"].get("text", ""),
            "score": res["score"]
        })

        context_blocks.append(
            f"=== CONTEXT_ID: {idx} ===\n"
            f"FILE: {res['payload'].get('filename')}\n"
            f"PAGE: {res['payload'].get('page')}\n\n"
            f"{res['payload'].get('text', '')}"
        )

    context_text = "\n\n".join(context_blocks)

    # -----------------------------
    # 5️⃣ Configure LLM
    # -----------------------------
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise RuntimeError("❌ GEMINI_API_KEY missing.")

    base_llm = llm or ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1,
    )

    structured_llm = base_llm.with_structured_output(RAGResponse)

    # -----------------------------
    # 6️⃣ Prompt with enforced citation rules
    # -----------------------------
    prompt = ChatPromptTemplate.from_template("""
Use only the following context when answering.

{context}

Rules:
- When citing, reference ONLY using the number shown after `CONTEXT_ID:` (example: 1, 2, 3).
- NEVER cite page numbers or filenames directly.
- NEVER guess citations.
- Return at most 2 citations.
- If unsure, return an empty citation list.

Return JSON ONLY in this shape:

{{
  "answer": "<your answer>",
  "citations": [
    {{ "context_id": 1 }}
  ]
}}

Question: {question}
""")

    chain = (
        {"context": lambda _: context_text, "question": RunnablePassthrough()}
        | prompt
        | structured_llm
    )

    # -----------------------------
    # 7️⃣ Execute LLM
    # -----------------------------
    response: RAGResponse = await asyncio.to_thread(chain.invoke, user_message)

    # -----------------------------
    # 8️⃣ Map citations to Qdrant metadata
    # -----------------------------
    formatted_sources = []
    used_pages = set()  # avoid duplicate pages


    if response.citations:
        for citation in response.citations[:3]: # make it 2 or 3 for top references

            # LLM sometimes outputs zero; convert to first item
            citation_id = citation.context_id if citation.context_id > 0 else 1

            match = next(
                (item for item in indexed_results if item["index"] == citation_id),
                None
            )

            if match:
                page = match["page"]

                # Skip duplicate pages if already included
                if page in used_pages:
                    continue
                used_pages.add(page)
                print(match, type(match), match.keys())

                formatted_sources.append({
                    "document": match["filename"],
                    "page": match["page"],
                    "excerpt": match["excerpt"][:200],
                    "relevance": round(float(match["score"]), 3),
                    "context_id": match["index"],
                })

    return response.answer, formatted_sources


# -----------------------------
# Helper: Load user documents
# -----------------------------
async def _get_user_documents(
    db: AsyncSession, user_id: str, document_id: str
) -> List[DocumentModel]:
    """Retrieve all documents belonging to a user."""
    stmt = (
        select(DocumentModel)
        .where(DocumentModel.owner_id == user_id)
        .where(DocumentModel.id == document_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
