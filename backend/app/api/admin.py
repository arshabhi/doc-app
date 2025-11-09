from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.crud import admin_crud
from app.db.schemas import admin as schemas
from app.core.dependencies import is_admin_user
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="", tags=["Admin"])

# 1. GET /api/admin/users
@router.get("/users")
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(is_admin_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    search: str | None = Query(None),
):
    skip = (page - 1) * limit
    rows = await admin_crud.get_all_users(db, skip, limit, search)

    data = []
    for user, doc_count, storage_used, chat_count in rows:
        data.append({
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": "admin" if user.is_superuser else "user",
            "status": "active" if user.is_active else "inactive",
            "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user.name or 'User'}",
            "createdAt": user.created_at,
            "lastLogin": user.updated_at,
            "stats": {
                "totalDocuments": int(doc_count or 0),
                "totalChats": int(chat_count or 0),
                "storageUsed": int(storage_used or 0),
                "lastActivity": user.updated_at,
            },
        })

    return {"success": True, "data": {"users": data}}

# 2. GET /api/admin/users/:id
@router.get("/users/{user_id}")
async def get_user_details(user_id: UUID, db: AsyncSession = Depends(get_db), current_admin=Depends(is_admin_user)):
    user = await admin_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    data = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": "admin" if user.is_superuser else "user",
        "status": "active" if user.is_active else "inactive",
        "preferences": user.preferences,
        "createdAt": user.created_at,
        "updatedAt": user.updated_at,
        "stats": {
            "totalDocuments": len(user.documents),
            "totalChats": len(user.sessions),
            "storageUsed": 0
        }
    }
    return {"success": True, "data": {"user": data}}

# 3. PUT /api/admin/users/:id
@router.put("/users/{user_id}")
async def update_user(user_id: UUID, payload: schemas.AdminUserUpdateRequest, db: AsyncSession = Depends(get_db), current_admin=Depends(is_admin_user)):
    user = await admin_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    for field, value in payload.dict(exclude_unset=True).items():
        if field == "role":
            user.is_superuser = value == "admin"
        elif field == "status":
            user.is_active = value == "active"
        else:
            setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return {"success": True, "data": {"user": {"id": user.id, "email": user.email, "name": user.name, "role": "admin" if user.is_superuser else "user"}}}

# 4. DELETE /api/admin/users/:id
@router.delete("/users/{user_id}")
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db), current_admin=Depends(is_admin_user)):
    if user_id == current_admin.id:
        raise HTTPException(400, detail={"code": "CANNOT_DELETE_SELF", "message": "You cannot delete your own account"})
    user = await admin_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    await admin_crud.delete_user(db, user)
    return {"success": True, "data": {"message": "User deleted successfully", "userId": str(user_id)}}

# 5. GET /api/admin/analytics
@router.get("/analytics")
async def get_analytics(db: AsyncSession = Depends(get_db), current_admin=Depends(is_admin_user), 
                        period: str = Query("month")):
    analytics = await admin_crud.get_system_analytics(db, period=period)
    return {"success": True, "data": {"analytics": analytics}}

# 6. GET /api/admin/documents
@router.get("/documents")
async def get_documents(db: AsyncSession = Depends(get_db), current_admin=Depends(is_admin_user)):
    docs = await admin_crud.get_all_documents(db)
    data = [{
        "id": d.id,
        "name": d.filename,
        "userId": d.owner_id,
        "uploadedAt": d.uploaded_at,
        "status": "processed",
        "size": len((d.meta_data or {}).get("text", "")),
    } for d in docs]
    return {"success": True, "data": {"documents": data}}

# 7. GET /api/admin/activity
@router.get("/activity")
async def get_activity(current_admin=Depends(is_admin_user)):
    # Stub data; in production, fetch from audit logs
    now = datetime.utcnow()
    data = [{
        "id": "act_1",
        "type": "document_upload",
        "userId": current_admin.id,
        "userName": current_admin.name,
        "description": "Uploaded a document",
        "timestamp": now,
        "metadata": {}
    }]
    return {"success": True, "data": {"activities": data}}

# 8. POST /api/admin/broadcast
@router.post("/broadcast")
async def send_broadcast(payload: schemas.BroadcastRequest, current_admin=Depends(is_admin_user)):
    broadcast_id = f"brd_{datetime.utcnow().timestamp()}"
    return {
        "success": True,
        "data": {
            "broadcastId": broadcast_id,
            "recipientCount": 87,
            "sentAt": datetime.utcnow(),
            "expiresAt": payload.expiresAt
        }
    }
