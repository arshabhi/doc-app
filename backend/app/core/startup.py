# app/core/startup.py
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import User
from app.core.security import hash_password
from app.core.config import settings
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels


ADMIN_EMAIL = settings.ADMIN_EMAIL
ADMIN_PASSWORD = settings.ADMIN_PASSWORD
ADMIN_NAME = settings.ADMIN_NAME


async def create_admin_user():
    async with AsyncSessionLocal() as session:  # type: AsyncSession
        q = await session.execute(select(User).where(User.email == ADMIN_EMAIL))
        existing = q.scalar_one_or_none()

        if existing:
            print(f"✅ Admin user already exists: {existing.email}")
            return

        # Create new admin
        admin_user = User(
            name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            is_active=True,
            is_superuser=True,
        )

        session.add(admin_user)
        await session.commit()
        print(f"🚀 Admin user created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")


async def init_qdrant():
    client = QdrantClient(url=settings.QDRANT_URL)
    collection = settings.QDRANT_COLLECTION_NAME

    collections = [c.name for c in client.get_collections().collections]
    if collection not in collections:
        client.create_collection(
            collection_name=collection,
            vectors_config=qmodels.VectorParams(
                size=settings.HUGGINGFACE_EMBEDDING_DIM,  # dimension for MiniLM-L6-v2
                distance=qmodels.Distance.COSINE,
            ),
        )
        print(f"🧠 Qdrant collection '{collection}' created.")
    else:
        client.delete_collection(collection_name=collection)
        client.create_collection(
            collection_name=collection,
            vectors_config=qmodels.VectorParams(
                size=settings.HUGGINGFACE_EMBEDDING_DIM,  # dimension for MiniLM-L6-v2
                distance=qmodels.Distance.COSINE,
            ),
        )
        print(f"✅ Qdrant collection '{collection}' already exists. Recreated")


async def startup_tasks():
    await create_admin_user()
    await init_qdrant()
