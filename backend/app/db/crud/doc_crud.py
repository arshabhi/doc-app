from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from app.db.models import Document
from uuid import UUID


async def get_user_documents(db: AsyncSession, user_id: UUID, limit: int = 20, offset: int = 0):
    q = select(Document).where(Document.owner_id == user_id).limit(limit).offset(offset)
    res = await db.execute(q)
    return res.scalars().all()


async def get_document_by_id(db: AsyncSession, doc_id: UUID):
    q = select(Document).where(Document.id == doc_id)
    res = await db.execute(q)
    return res.scalars().first()


async def update_document_metadata(db: AsyncSession, doc_id: UUID, metadata: dict):
    q = (
        update(Document)
        .where(Document.id == doc_id)
        .values(meta_data=Document.meta_data.op("||")(metadata))
        .returning(Document)
    )
    res = await db.execute(q)
    await db.commit()
    return res.scalar_one_or_none()


async def delete_document(db: AsyncSession, doc_id: UUID):
    await db.execute(delete(Document).where(Document.id == doc_id))
    await db.commit()
