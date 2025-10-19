# app/db/crud/chat_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import ChatSession, Message
from uuid import UUID
from datetime import datetime

async def create_session(db: AsyncSession, user_id: UUID, name: str = "Conversation"):
    session = ChatSession(user_id=user_id, name=name, created_at=datetime.utcnow())
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

async def log_message(db: AsyncSession, user_id: UUID, session_id: UUID, user_content: str, assistant_content: str):
    # ensure session exists or create
    q = select(ChatSession).where(ChatSession.id == session_id)
    res = await db.execute(q)
    sess = res.scalars().first()
    if not sess:
        sess = await create_session(db, user_id)
        session_id = sess.id

    # store user message
    user_msg = Message(session_id=session_id, role="user", content=user_content, created_at=datetime.utcnow())
    assistant_msg = Message(session_id=session_id, role="assistant", content=assistant_content, created_at=datetime.utcnow())

    db.add_all([user_msg, assistant_msg])
    await db.commit()
    return {"session_id": session_id}
