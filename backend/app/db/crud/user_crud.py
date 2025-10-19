# app/db/crud/user_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import User
from uuid import UUID

async def get_by_email(db: AsyncSession, email: str):
    q = select(User).where(User.email == email)
    res = await db.execute(q)
    return res.scalars().first()

async def create_user(db: AsyncSession, email: str, hashed_password: str):
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_by_id(db: AsyncSession, user_id: UUID):
    q = select(User).where(User.id == user_id)
    res = await db.execute(q)
    return res.scalars().first()
