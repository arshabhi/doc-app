# app/services/document_service.py

import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Document


async def process_and_store_document(
    db: AsyncSession,
    owner_id: str,
    filename: str,
    content: str,
    metadata: dict = None
):
    """
    Processes an uploaded document and stores it in the database.
    """
    metadata = metadata or {}

    # Ensure consistent JSON structure for `meta_data`
    doc = Document(
        owner_id=owner_id,
        filename=filename,
        meta_data={"text": content.strip(), **metadata},
        uploaded_at=datetime.utcnow(),
    )

    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc

