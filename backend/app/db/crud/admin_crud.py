from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import User, Document, ChatSession, Comparison
from typing import List, Optional
from uuid import UUID

# Get all users
async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 20, search: Optional[str] = None):
    q = select(User)
    if search:
        q = q.where(User.email.ilike(f"%{search}%") | User.name.ilike(f"%{search}%"))
    q = q.offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()

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
