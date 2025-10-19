# app/db/crud/doc_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Document
from sqlalchemy import select
from uuid import UUID
from datetime import datetime

async def create_document(db: AsyncSession, owner_id: UUID, filename: str, content_type: str, metadata: dict):
    doc = Document(owner_id=owner_id, filename=filename, content_type=content_type, meta_data=metadata, uploaded_at=datetime.utcnow())
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc

async def get_user_documents(db: AsyncSession, owner_id: UUID):
    q = select(Document).where(Document.owner_id == owner_id).order_by(Document.uploaded_at.desc())
    res = await db.execute(q)
    return res.scalars().all()

async def get_document(db: AsyncSession, doc_id: UUID):
    q = select(Document).where(Document.id == doc_id)
    res = await db.execute(q)
    return res.scalars().first()
