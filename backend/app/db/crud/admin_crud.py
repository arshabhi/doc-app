from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.models import User, Document, ChatSession, Comparison
from typing import List, Optional
from uuid import UUID

# Get all users
async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 20, search: str = None):
    # Subqueries for counts
    doc_counts = (
        select(Document.owner_id, func.count().label("doc_count"))
        .group_by(Document.owner_id)
        .subquery()
    )

    chat_counts = (
        select(ChatSession.user_id, func.count().label("chat_count"))
        .group_by(ChatSession.user_id)
        .subquery()
    )

    # Base query joining aggregated counts
    query = (
        select(
            User,
            func.coalesce(doc_counts.c.doc_count, 0).label("doc_count"),
            func.coalesce(chat_counts.c.chat_count, 0).label("chat_count")
        )
        .outerjoin(doc_counts, User.id == doc_counts.c.owner_id)
        .outerjoin(chat_counts, User.id == chat_counts.c.user_id)
    )

    # Apply search filter
    if search:
        query = query.where(
            or_(
                User.email.ilike(f"%{search}%"),
                User.name.ilike(f"%{search}%")
            )
        )

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    return result.all()

# Get user by id
async def get_user_by_id(db: AsyncSession, user_id: UUID):
    q = select(User).where(User.id == user_id)
    result = await db.execute(q)
    return result.scalars().first()

# Delete user and cascade
async def delete_user(db: AsyncSession, user: User):
    await db.delete(user)
    await db.commit()

# Get all documents
async def get_all_documents(db: AsyncSession, skip=0, limit=20):
    q = select(Document).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()

# Simple analytics mock
async def get_system_analytics(db: AsyncSession):
    total_users = (await db.execute(select(func.count(User.id)))).scalar()
    total_docs = (await db.execute(select(func.count(Document.id)))).scalar()
    total_chats = (await db.execute(select(func.count(ChatSession.id)))).scalar()
    total_comparisons = (await db.execute(select(func.count(Comparison.id)))).scalar()
    return {
        "period": "month",
        "users": {"total": total_users, "active": total_users, "new": 5},
        "documents": {"total": total_docs},
        "chats": {"total": total_chats},
        "comparisons": {"total": total_comparisons},
        "summaries": {"total": 0},
        "performance": {"systemUptime": 99.8},
        "engagement": {"dailyActiveUsers": 40},
        "topUsers": [],
        "systemHealth": {"status": "healthy"}
    }
