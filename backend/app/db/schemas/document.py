# app/db/schemas/document.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class DocumentOut(BaseModel):
    id: UUID
    filename: str
    content_type: str
    uploaded_at: datetime
    metadata: Optional[dict] = {}

    class Config:
        orm_mode = True
