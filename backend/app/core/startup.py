# app/core/startup.py

import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import User
from app.core.security import hash_password
from app.core.config import settings

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.utils.async_minio import async_minio


ADMIN_EMAIL = settings.ADMIN_EMAIL
ADMIN_PASSWORD = settings.ADMIN_PASSWORD
ADMIN_NAME = settings.ADMIN_NAME


async def create_admin_user():
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(User).where(User.email == ADMIN_EMAIL))
        existing = q.scalar_one_or_none()

        if existing:
            print(f"✅ Admin already exists: {existing.email}")
            return

        user = User(
            name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            is_active=True,
            is_superuser=True,
        )

        session.add(user)
        await session.commit()

        print(f"🚀 Admin created: {ADMIN_EMAIL}")


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

async def init_minio():
    await async_minio.ensure_bucket_exists(settings.MINIO_DOCUMENT_BUCKET)
    print(f"🪣 MinIO bucket ensured: {settings.MINIO_DOCUMENT_BUCKET}")


async def startup_tasks():
    await create_admin_user()
    await init_qdrant()
    await init_minio()
