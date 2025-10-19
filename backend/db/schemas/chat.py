# app/db/schemas/chat.py
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class ChatRequest(BaseModel):
    session_id: Optional[UUID] = None
    message: str

class ChatResponse(BaseModel):
    session_id: Optional[UUID]
    user_message: str
    assistant_message: str
    sources: Optional[List[dict]] = []
