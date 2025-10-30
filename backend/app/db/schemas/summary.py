from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict
from datetime import datetime

class SummaryOptions(BaseModel):
    length: str
    style: str
    focusAreas: Optional[List[str]] = []
    language: Optional[str] = "en"

class SummaryCreateRequest(BaseModel):
    documentId: str
    options: SummaryOptions

class SummaryResponse(BaseModel):
    id: str
    document_id: str
    style: str
    length: Optional[str]
    content: str
    key_points: List[str]
    word_count: int
    confidence: float
    created_at: datetime
    meta_data: Dict

    model_config = ConfigDict(from_attributes=True)
