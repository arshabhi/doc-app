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
    content: dict,
    size: int,
    metadata: dict = None,
):
    """
    1. Store doc metadata in DB
    2. Split + embed content
    3. Store embeddings in Qdrant

    Expects `content` structure like:
    {
        "extension": "pdf",
        "pages": [
            {"page": 1, "content": "..."},
            {"page": 2, "content": "..."}
        ]
    }
    """
    # Validate structure
    if not content or "pages" not in content or len(content["pages"]) == 0:
        raise ValueError("❌ Cannot process: structured content is empty or invalid.")

    metadata = metadata or {}

    # 1️⃣ Store document metadata & structured content (FULL JSON preserved)
    doc = Document(
        owner_id=uuid.UUID(str(owner_id)),
        filename=filename,
        content_type=content_type,
        uploaded_at=datetime.utcnow(),
        size=size,
        meta_data={"structure": content, **metadata},  # keep structured JSON
    )

    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # 2️⃣ Prepare embeddings
    embedding_model = HuggingFaceEmbeddings(model_name=settings.HUGGINGFACE_EMBEDDING_MODEL)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    # Instead of splitting whole document blindly, split page-by-page
    chunks = []
    for page in content["pages"]:
        page_text = page["content"].strip()
        if not page_text:
            continue

        page_chunks = splitter.split_text(page_text)

        for chunk in page_chunks:
            chunks.append({"page": page["page"], "content": chunk})

    # 3️⃣ Compute embeddings
    vectors = await asyncio.to_thread(
        embedding_model.embed_documents, 
        [c["content"] for c in chunks]
    )

    # 4️⃣ Insert into Qdrant with page awareness
    payloads = [
        {
            "document_id": str(doc.id),
            "owner_id": str(owner_id),
            "chunk_index": idx,
            "page": chunk["page"],
            "filename": filename,
            "text": chunk["content"],
        }
        for idx, chunk in enumerate(chunks)
    ]

    await upsert_vectors(vectors=vectors, payloads=payloads)

    return doc
