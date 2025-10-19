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
    """
    Uploads a document, stores content and metadata in the database.
    """
    try:
        content = await file.read()
        content_str = content.decode("utf-8")  # or "latin-1" if needed
        result = await process_and_store_document(
            db=db,
            owner_id=current_user.id,
            filename=file.filename,
            content=content_str,
            metadata={}
        )
        return {"status": "success", "details": {"id": str(result.id), "filename": result.filename}}
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
