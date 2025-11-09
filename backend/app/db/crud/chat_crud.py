# app/db/crud/chat_crud.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.models import ChatSession, Message
from uuid import UUID
from datetime import datetime


# ------------------------------------------------------
# Create or fetch a chat session
# ------------------------------------------------------
async def create_session(
    db: AsyncSession,
    user_id: UUID,
    name: str = "Conversation",
    document_id: UUID | None = None
):
    session = ChatSession(
        user_id=user_id,
        name=name,
        document_id=document_id,
        created_at=datetime.utcnow()
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


# ------------------------------------------------------
# Log user + assistant messages into session
# ------------------------------------------------------
# app/db/crud/chat_crud.py
async def log_message(
    db: AsyncSession,
    user_id: UUID,
    session_id: UUID,
    user_content: str,
    assistant_content: str,
    document_id: Optional[UUID] = None
):
    # Try existing session
    q = select(ChatSession).where(ChatSession.id == session_id)
    res = await db.execute(q)
    sess = res.scalars().first()

    if not sess:
        sess = ChatSession(
            user_id=user_id,
            document_id=document_id,   # ✅ link to document
            name="Conversation"
        )
        db.add(sess)
        await db.commit()
        await db.refresh(sess)
        session_id = sess.id

    # Store both user & assistant messages
    user_msg = Message(session_id=session_id, role="user", content=user_content)
    assistant_msg = Message(session_id=session_id, role="assistant", content=assistant_content)
    db.add_all([user_msg, assistant_msg])
    await db.commit()

    return {"session_id": session_id}

# ------------------------------------------------------
# Get all messages for a document
# ------------------------------------------------------
async def get_history_by_document(db: AsyncSession, user_id: UUID, document_id: UUID):
    q = (
        select(Message)
        .join(ChatSession, ChatSession.id == Message.session_id)
        .where(ChatSession.user_id == user_id, ChatSession.document_id == document_id)
        .order_by(Message.created_at.asc())
    )
    res = await db.execute(q)
    return res.scalars().all()


# ------------------------------------------------------
# Delete all messages for a document
# ------------------------------------------------------
async def delete_history_by_document(db: AsyncSession, user_id: UUID, document_id: UUID):
    q = select(ChatSession).where(
        ChatSession.user_id == user_id,
        ChatSession.document_id == document_id
    )
    sessions = (await db.execute(q)).scalars().all()
    if not sessions:
        return False

    for s in sessions:
        await db.delete(s)
    await db.commit()
    return True


# ------------------------------------------------------
# List all chat conversations for a user
# ------------------------------------------------------
async def list_conversations(db: AsyncSession, user_id: UUID):
    q = select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc())
    res = await db.execute(q)
    return res.scalars().all()
