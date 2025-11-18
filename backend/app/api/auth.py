from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
from app.db.session import get_db
from app.db.crud import user_crud
from app.db.schemas.user import LogoutRequest, UserCreate, UserLogin, TokenResponse, UserResponse
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    hash_password,
    decode_token,
)
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Utility function to standardize responses
def success_response(data: dict, status_code: int = 200):
    return {"success": True, "data": data}


def error_response(code: str, message: str, status_code: int):
    raise HTTPException(
        status_code=status_code,
        detail={"success": False, "error": {"code": code, "message": message}},
    )


# ============================================================
# 1️⃣ Register
# ============================================================
@router.post("/register", status_code=201)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await user_crud.get_by_email(db, user.email)
    if existing_user:
        error_response("EMAIL_ALREADY_EXISTS", "An account with this email already exists", 400)

    hashed_pw = hash_password(user.password)
    new_user = await user_crud.create_user(db, user.email, hashed_pw, name=user.name)

    access_token = create_access_token({"sub": new_user.email})
    refresh_token = create_refresh_token({"sub": new_user.email})

    response = {
        "user": {
            "id": f"usr_{new_user.id}",
            "email": new_user.email,
            "name": new_user.name,
            # "role": new_user.role,
            "createdAt": new_user.created_at.isoformat(),
            "updatedAt": new_user.updated_at.isoformat(),
        },
        "tokens": {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        },
    }
    return success_response(response, status_code=201)


# ============================================================
# 2️⃣ Login
# ============================================================
@router.post("/login", status_code=200)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        error_response("INVALID_CREDENTIALS", "Invalid email or password", 401)

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    response = {
        "user": {
            "id": f"usr_{user.id}",
            "email": user.email,
            "name": user.name,
            "role": "admin" if user.is_superuser else "user",
            "createdAt": user.created_at.isoformat(),
            "updatedAt": user.updated_at.isoformat(),
        },
        "tokens": {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        },
    }
    return success_response(response)


# ============================================================
# 3️⃣ Logout
# ============================================================
@router.post("/logout", status_code=200)
async def logout(payload: LogoutRequest, token: str = Depends(oauth2_scheme)):
    # In stateless JWT, we can’t truly "invalidate" a token unless using a DB blacklist
    # Here we just simulate success
    return success_response({"message": "Logged out successfully"})


# ============================================================
# 4️⃣ Get Current User (/me)
# ============================================================
@router.get("/me", status_code=200)
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email:
            error_response("INVALID_TOKEN", "Invalid access token", 401)

        user = await user_crud.get_by_email(db, email)
        if not user:
            error_response("USER_NOT_FOUND", "User not found", 404)

        user_data = {
            "id": f"usr_{user.id}",
            "email": user.email,
            "name": user.name,
            "role": "admin" if user.is_superuser else "user",
            "status": "active" if user.is_active else "inactive",
            "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user.name or 'user'}",
            "createdAt": user.created_at.isoformat(),
            "updatedAt": user.updated_at.isoformat(),
            "preferences": {
                "theme": "light",
                "language": "en",
                "notifications": True,
            },
            "stats": {
                "totalDocuments": 15,
                "totalChats": 42,
                "storageUsed": 1048576,
            },
        }
        return success_response({"user": user_data})
    except Exception:
        error_response("INVALID_TOKEN", "Invalid or expired access token", 401)


# ============================================================
# 5️⃣ Refresh Token
# ============================================================
@router.post("/refresh", status_code=200)
async def refresh_token_endpoint(body: dict):
    refresh_token = body.get("refreshToken")
    if not refresh_token:
        error_response("MISSING_REFRESH_TOKEN", "Refresh token is required", 400)

    try:
        payload = decode_token(refresh_token)
        email = payload.get("sub")
        if not email:
            error_response("INVALID_REFRESH_TOKEN", "Invalid refresh token", 401)

        new_access_token = create_access_token({"sub": email})
        response = {
            "accessToken": new_access_token,
            "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        }
        return success_response(response)
    except Exception:
        error_response("INVALID_REFRESH_TOKEN", "Invalid or expired refresh token", 401)


@router.post("/login-form", response_model=TokenResponse)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint for Swagger UI and OAuth2Password flow.
    - `username` field → user's email
    - `password` field → user's password
    """
    user = await user_crud.get_by_email(db, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
