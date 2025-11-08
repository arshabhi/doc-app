# app/services/document_service.py

import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Document
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
# from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings
import asyncio
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.utils.qdrant import upsert_vectors


async def process_and_store_document(
    db: AsyncSession,
    owner_id: uuid.UUID,
    filename: str,
    content: str,
    size: int,
    metadata: dict = None,
):
    """
    Processes an uploaded document:
      1. Stores metadata in the database.
      2. Splits and embeds content using SentenceTransformer (MiniLM).
      3. Stores embeddings + metadata into Qdrant.
    """

    if not content or not content.strip():
        raise ValueError("❌ Empty document content — cannot process.")

    metadata = metadata or {}

    # 1️⃣ Store document record in DB
    doc = Document(
        owner_id=uuid.UUID(str(owner_id)),
        filename=filename,
        meta_data={"text": content.strip(), **metadata},
        uploaded_at=datetime.utcnow(),
        size=size,
    )

    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # 2️⃣ Initialize SentenceTransformer embeddings
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Split into manageable chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_text(content.strip())

    # Compute embeddings asynchronously (offload to thread pool)
    vectors = await asyncio.to_thread(embedding_model.embed_documents, chunks)

    payloads = [{
                "document_id": str(doc.id),
                "owner_id": str(owner_id),
                "chunk_index": idx,
                "filename": filename,
                "text": chunk,
            } for idx, chunk in enumerate(chunks)]
    
    upsert_vectors(vectors=vectors, payloads=payloads)

    # 3️⃣ Push to Qdrant
    # qclient = QdrantClient(url=settings.QDRANT_URL)

    # points = [
    #     qmodels.PointStruct(
    #         id=str(uuid.uuid4()),
    #         vector=vector,
    #         payload={
    #             "document_id": str(doc.id),
    #             "owner_id": str(owner_id),
    #             "chunk_index": idx,
    #             "filename": filename,
    #             "text": chunk,
    #         },
    #     )
    #     for idx, (chunk, vector) in enumerate(zip(chunks, vectors))
    # ]

    # # Run Qdrant upsert off the main event loop
    # await asyncio.to_thread(
    #     qclient.upsert,
    #     collection_name=settings.QDRANT_COLLECTION_NAME,
    #     points=points,
    # )

    # print(f"📄 Stored {len(chunks)} chunks from '{filename}' into Qdrant.")

    return doc

