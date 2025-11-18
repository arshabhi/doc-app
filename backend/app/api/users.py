# app/api/users.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.crud import user_crud
from app.core.security import get_current_user
from app.db.schemas.user import UserOut

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_profile(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Fetch current user profile info
    """
    return await user_crud.get_by_email(db, current_user.email)
