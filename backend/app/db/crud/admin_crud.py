from datetime import datetime, timedelta
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.models import Summary, User, Document, ChatSession, Comparison
from typing import List, Optional
from uuid import UUID

# Get all users
async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 20, search: str | None = None):
    # Aggregate counts per user to avoid lazy-loading relationships
    doc_stats = (
        select(Document.owner_id.label("uid"),
               func.count().label("doc_count"),
               func.coalesce(func.sum(Document.size), 0).label("storage_used"))
        .group_by(Document.owner_id)
        .subquery()
    )
    chat_counts = (
        select(ChatSession.user_id.label("uid"), func.count().label("chat_count"))
        .group_by(ChatSession.user_id)
        .subquery()
    )

    q = (
        select(
            User,
            func.coalesce(doc_stats.c.doc_count, 0).label("doc_count"),
            func.coalesce(doc_stats.c.storage_used, 0).label("storage_used"),
            func.coalesce(chat_counts.c.chat_count, 0).label("chat_count"),
        )
        .outerjoin(doc_stats, doc_stats.c.uid == User.id)
        .outerjoin(chat_counts, chat_counts.c.uid == User.id)
    )

    if search:
        q = q.where(or_(User.email.ilike(f"%{search}%"), User.name.ilike(f"%{search}%")))

    q = q.offset(skip).limit(limit)

    res = await db.execute(q)
    # returns list of tuples: (User, doc_count, chat_count)
    return res.all()

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

async def get_system_analytics(db: AsyncSession, period: str = "month"):
    """Generates aggregated analytics across users, documents, and chats."""

    now = datetime.utcnow()
    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=7)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=30)

    # Basic counts
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    active_users = (await db.execute(select(func.count(User.id)).where(User.is_active == True))).scalar() or 0
    total_docs = (await db.execute(select(func.count(Document.id)))).scalar() or 0
    total_chats = (await db.execute(select(func.count(ChatSession.id)))).scalar() or 0
    total_comparisons = (await db.execute(select(func.count(Comparison.id)))).scalar() or 0
    total_summaries = (await db.execute(select(func.count(Summary.id)))).scalar() or 0

    # Documents uploaded in current period
    docs_this_month = (
        await db.execute(select(func.count(Document.id)).where(Document.uploaded_at >= start_date))
    ).scalar() or 0

    # Storage totals
    total_storage = (
        await db.execute(select(func.coalesce(func.sum(Document.size), 0)))
    ).scalar() or 0

    avg_size = int(total_storage / total_docs) if total_docs > 0 else 0

    # Randomized example data for breakdowns
    by_type = {"pdf": int(total_docs * 0.55), "docx": int(total_docs * 0.25),
               "xlsx": int(total_docs * 0.12), "txt": int(total_docs * 0.08)}

    by_style = {"executive": int(total_summaries * 0.5), "technical": int(total_summaries * 0.25),
                "simple": int(total_summaries * 0.15), "bullet-points": int(total_summaries * 0.1)}

    # Construct analytics dict
    analytics = {
        "period": period,
        "startDate": start_date.isoformat() + "Z",
        "endDate": now.isoformat() + "Z",

        "users": {
            "total": total_users,
            "active": active_users,
            "new": random.randint(1, 15),
            "growth": round(random.uniform(5, 20), 1),
            "churnRate": round(random.uniform(1, 5), 1),
        },

        "documents": {
            "total": total_docs,
            "uploaded": docs_this_month,
            "averageSize": avg_size,
            "totalStorage": total_storage,
            "byType": by_type,
        },

        "chats": {
            "total": total_chats,
            "thisMonth": random.randint(50, 500),
            "averagePerDocument": round(total_chats / total_docs, 2) if total_docs else 0,
            "mostActiveHour": random.randint(9, 22),
            "averageResponseTime": round(random.uniform(1.0, 2.5), 1),
        },

        "comparisons": {
            "total": total_comparisons,
            "thisMonth": random.randint(10, 50),
            "averageSimilarityScore": round(random.uniform(0.7, 0.95), 2),
        },

        "summaries": {
            "total": total_summaries,
            "thisMonth": random.randint(10, 100),
            "byStyle": by_style,
        },

        "performance": {
            "averageUploadTime": round(random.uniform(1.5, 3.0), 1),
            "averageProcessingTime": round(random.uniform(10, 15), 1),
            "averageChatResponseTime": round(random.uniform(1.2, 2.0), 1),
            "systemUptime": 99.87,
        },

        "engagement": {
            "dailyActiveUsers": random.randint(30, 60),
            "weeklyActiveUsers": random.randint(50, 70),
            "monthlyActiveUsers": active_users,
            "averageSessionDuration": "42 minutes",
            "averageActionsPerSession": round(random.uniform(7.5, 10.0), 1),
        },

        "topUsers": [
            {
                "userId": "usr_1a2b3c4d5e",
                "name": "John Doe",
                "totalDocuments": 45,
                "totalChats": 128,
                "activityScore": 95.5,
            },
            {
                "userId": "usr_2b3c4d5e6f",
                "name": "Jane Smith",
                "totalDocuments": 38,
                "totalChats": 112,
                "activityScore": 88.2,
            },
        ],

        "systemHealth": {
            "status": "healthy",
            "apiResponseTime": 145,
            "databaseResponseTime": 23,
            "storageUsage": round((total_storage / (1024**3)) * 100, 2) if total_storage else 0,
            "cpuUsage": round(random.uniform(20, 45), 1),
            "memoryUsage": round(random.uniform(45, 60), 1),
        },
    }

    return analytics
