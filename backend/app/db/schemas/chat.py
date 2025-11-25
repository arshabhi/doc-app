# app/db/schemas/chat.py
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# ===========================================================
# Core Request / Response Models
# ===========================================================


class ChatRequest(BaseModel):
    session_id: Optional[UUID] = None
    message: str
    document_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    session_id: Optional[UUID]
    user_message: str
    assistant_message: str
    sources: Optional[List[dict]] = []


# ===========================================================
# Message / History Models
# ===========================================================


class MessageSchema(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True


class ChatHistoryResponse(BaseModel):
    document_id: UUID
    messages: List[MessageSchema]


# ===========================================================
# Conversation Listing Models
# ===========================================================


class ConversationSchema(BaseModel):
    session_id: UUID
    name: str
    created_at: datetime
    document_id: Optional[UUID]

    class Config:
        orm_mode = True


class ConversationListResponse(BaseModel):
    conversations: List[ConversationSchema]
