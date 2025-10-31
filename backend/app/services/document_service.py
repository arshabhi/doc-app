# app/services/document_service.py

from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Document


async def process_and_store_document(
    db: AsyncSession,
    owner_id: UUID,
    filename: str,
    content: str,
    size: int,
    metadata: dict = None
):
    """
    Processes an uploaded document and stores it in the database.
    """
    metadata = metadata or {}

    # Ensure consistent JSON structure for `meta_data`
    doc = Document(
        owner_id=UUID(str(owner_id)),
        filename=filename,
        meta_data={"text": content.strip(), **metadata},
        uploaded_at=datetime.utcnow(),
        size=size
    )

    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc

