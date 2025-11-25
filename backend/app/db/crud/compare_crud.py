from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID, uuid4
from datetime import datetime
from app.db.models import Comparison


async def create_comparison(
    db: AsyncSession,
    user_id: UUID,
    document_id_1: UUID,
    document_id_2: UUID,
    comparison_type: str,
    meta_data: dict = None,
):
    comparison = Comparison(
        id=uuid4(),
        user_id=user_id,
        document_id1=document_id_1,
        document_id2=document_id_2,
        comparison_type=comparison_type,
        status="processing",
        meta_data=meta_data or {},
        created_at=datetime.utcnow(),
    )
    db.add(comparison)
    await db.commit()
    await db.refresh(comparison)
    return comparison


async def get_comparison_by_id(db: AsyncSession, comparison_id: UUID):
    result = await db.execute(select(Comparison).where(Comparison.id == comparison_id))
    return result.scalars().first()


async def get_comparison_history(
    db: AsyncSession, user_id: UUID, document_id: UUID = None, limit: int = 20, offset: int = 0
):
    query = (
        select(Comparison)
        .where(Comparison.user_id == user_id)
        .order_by(Comparison.created_at.desc())
    )
    if document_id:
        query = query.where(
            (Comparison.document_id_1 == document_id) | (Comparison.document_id_2 == document_id)
        )
    result = await db.execute(query.limit(limit).offset(offset))
    return result.scalars().all()


async def delete_comparison(db: AsyncSession, comparison_id: UUID):
    await db.execute(delete(Comparison).where(Comparison.id == comparison_id))
    await db.commit()
    return True
