# app/db/crud/chat_crud.py
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
async def log_message(
    db: AsyncSession,
    user_id: UUID,
    session_id: UUID | None,
    user_content: str,
    assistant_content: str,
    document_id: UUID | None = None
):
    # Ensure session exists or create new one
    if session_id:
        q = select(ChatSession).where(ChatSession.id == session_id)
        res = await db.execute(q)
        session = res.scalars().first()
    else:
        session = None

    if not session:
        session = await create_session(db, user_id, document_id=document_id)
        session_id = session.id

    # Create message pairs
    user_msg = Message(session_id=session_id, role="user", content=user_content, created_at=datetime.utcnow())
    assistant_msg = Message(session_id=session_id, role="assistant", content=assistant_content, created_at=datetime.utcnow())

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
