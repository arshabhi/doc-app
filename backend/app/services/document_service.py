# app/services/document_service.py

import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings
import asyncio
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.utils.qdrant import upsert_vectors  # ensure this is async or threaded!


async def process_and_store_document(
    db: AsyncSession,
    owner_id: uuid.UUID,
    filename: str,
    content_type: str,
    content: str,
    size: int,
    metadata: dict = None,
):
    """
    1. Store doc metadata in DB
    2. Split + embed content
    3. Store embeddings in Qdrant
    """

    if not content or not content.strip():
        raise ValueError("❌ Empty document content — cannot process.")

    metadata = metadata or {}

    # 1️⃣ Store document record in DB
    doc = Document(
    owner_id=uuid.UUID(str(owner_id)),
    filename=filename,
    content_type=content_type,     # <-- add
    meta_data={"text": content.strip(), **metadata},
    uploaded_at=datetime.utcnow(),
    size=size,
)


    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # 2️⃣ Initialize embeddings
    embedding_model = HuggingFaceEmbeddings(model_name=settings.HUGGINGFACE_EMBEDDING_MODEL)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_text(content.strip())

    # 3️⃣ Compute embeddings (in thread pool)
    vectors = await asyncio.to_thread(embedding_model.embed_documents, chunks)

    payloads = [
        {
            "document_id": str(doc.id),
            "owner_id": str(owner_id),
            "chunk_index": idx,
            "filename": filename,
            "text": chunk,
        }
        for idx, chunk in enumerate(chunks)
    ]

    # 4️⃣ Upsert into Qdrant (ensure async or thread execution inside)
    await upsert_vectors(vectors=vectors, payloads=payloads)

    return doc
