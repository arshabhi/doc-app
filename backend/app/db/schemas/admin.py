from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal, Union, Dict
from uuid import UUID
from datetime import datetime

# ---- User-related ----
class AdminUserStats(BaseModel):
    totalDocuments: int
    totalChats: int
    totalComparisons: int
    totalSummaries: int
    storageUsed: int
    storageLimit: Optional[int] = None
    lastActivity: Optional[datetime] = None

class AdminUserBase(BaseModel):
    id: UUID
    email: EmailStr
    name: Optional[str]
    role: Literal["user", "admin"]
    status: Literal["active", "inactive"]
    avatar: Optional[str]
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    lastLogin: Optional[datetime] = None

class AdminUserDetail(AdminUserBase):
    preferences: Optional[dict] = None
    stats: Optional[AdminUserStats] = None

class AdminUserUpdateRequest(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    role: Optional[Literal["user", "admin"]]
    status: Optional[Literal["active", "inactive"]]
    storageLimit: Optional[int]

class AdminUserDeleteResponse(BaseModel):
    success: bool
    data: dict

# ---- Analytics ----
class AnalyticsData(BaseModel):
    period: str
    users: dict
    documents: dict
    chats: dict
    comparisons: dict
    summaries: dict
    performance: dict
    engagement: dict
    topUsers: list
    systemHealth: dict

# ---- Document List ----
class AdminDocument(BaseModel):
    id: UUID
    name: str
    size: int
    mimeType: Optional[str]
    userId: UUID
    userName: Optional[str]
    status: str
    uploadedAt: datetime
    tags: Optional[List[str]] = []

# ---- Activity ----
class AdminActivity(BaseModel):
    id: UUID
    type: str
    userId: UUID
    userName: str
    description: str
    timestamp: datetime
    metadata: Optional[dict] = {}

# ---- Broadcast ----
class BroadcastRequest(BaseModel):
    title: str
    message: str
    recipients: Union[Literal["all", "active", "inactive"], List[UUID]]
    type: Literal["info", "warning", "alert"]
    expiresAt: datetime

class BroadcastResponse(BaseModel):
    success: bool
    data: dict
