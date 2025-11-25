from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user


async def is_admin_user(current_user=Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
