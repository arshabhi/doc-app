# app/db/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime

# Base user fields
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


# Request schemas
class UserCreate(UserBase):
    password: str
    confirmPassword: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class LogoutRequest(BaseModel):
    refreshToken: str

# Response schemas
class UserOut(UserBase):
    id: UUID
    role: Optional[str] = "user"
    is_active: Optional[bool] = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    id: UUID
    name: Optional[str]
    email: EmailStr
    role: Optional[str] = "user"
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime]
    avatar_url: Optional[HttpUrl] = None
    preferences: Optional[Dict[str, Any]] = None
    stats: Optional[Dict[str, Any]] = None  # for future: total_docs, sessions, etc.

    class Config:
        orm_mode = True

class TokenData(BaseModel):
    accessToken: str
    refreshToken: str
    expiresIn: int = Field(default=3600)


# Standard API response models
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict
