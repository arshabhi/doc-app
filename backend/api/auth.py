# app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.db.session import get_db
from app.db.models import User
from app.core.security import create_access_token, create_refresh_token, verify_password, hash_password
from app.db.crud import user_crud
from app.db.schemas.user import UserCreate, UserLogin, TokenResponse
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await user_crud.get_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = hash_password(user.password)
    new_user = await user_crud.create_user(db, user.email, hashed_pw)
    access_token = create_access_token({"sub": new_user.email})
    refresh_token = create_refresh_token({"sub": new_user.email})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    payload = await create_access_token_from_refresh(refresh_token)
    return TokenResponse(**payload)
