# app/api/documents.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.document_service import process_and_store_document
from app.core.security import get_current_user

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        result = await process_and_store_document(file, current_user.id, db)
        return {"status": "success", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

@router.get("/list")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    from app.db.crud import doc_crud
    docs = await doc_crud.get_user_documents(db, current_user.id)
    return docs
