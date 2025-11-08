# app/core/startup.py
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import User
from app.core.security import hash_password
from app.core.config import settings


ADMIN_EMAIL = "admin@example.com"      # ✅ You can load from ENV too
ADMIN_PASSWORD = "Admin@123"           # ✅ Change for production!
ADMIN_NAME = "System Admin"


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
            role="admin"
        )

        session.add(admin_user)
        await session.commit()
        print(f"🚀 Admin user created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
