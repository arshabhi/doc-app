from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.db.models import Document
from app.db.crud import doc_crud
from app.services.document_service import process_and_store_document
from app.core.security import get_current_user
from uuid import UUID
from app.processing.extract_content import extract_content

router = APIRouter(tags=["Documents"])


# ---------------------------
# POST /upload
# ---------------------------
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Upload and process a new document."""
    try:
        size = file.size
        # content = await file.read()
        # content_str = content.decode("utf-8", errors="ignore")
        content = extract_content(file)

        result = await process_and_store_document(
            db=db,
            owner_id=current_user.id,
            filename=file.filename,
            content=content["content"],
            size=size,
            metadata={},
        )
        # return {"status": "success", "details": {"id": str(result.id), "filename": result.filename}}
        return {"status": "success", "document": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


# ---------------------------
# GET /list
# ---------------------------
@router.get("/list")
async def list_documents(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    docs = await doc_crud.get_user_documents(db, current_user.id, limit=limit, offset=offset)

    return {
        "success": True,
        "data": {
            "documents": [
                {
                    "id": str(doc.id),
                    "name": doc.filename,
                    "uploadedAt": doc.uploaded_at,
                    "mimeType": doc.content_type,
                    "extractedText": doc.meta_data.get("text") if doc.meta_data else None,
                    "summary": doc.meta_data.get("summary") if doc.meta_data else None,
                    "status": "completed",
                    "url": f"/api/documents/{doc.id}/download",
                }
                for doc in docs
            ]
        },
    }


# ---------------------------
# GET /{id}
# ---------------------------
@router.get("/{id}")
async def get_document(
    id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get details of a specific document."""
    doc = await doc_crud.get_document_by_id(db, id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


# ---------------------------
# PUT /{id}
# ---------------------------
@router.put("/{id}")
async def update_document(
    id: UUID,
    metadata: dict,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update document metadata."""
    doc = await doc_crud.get_document_by_id(db, id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    updated_doc = await doc_crud.update_document_metadata(db, id, metadata)
    return {"status": "success", "updated": updated_doc}


# ---------------------------
# DELETE /{id}
# ---------------------------
@router.delete("/{id}")
async def delete_document(
    id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete a document."""
    doc = await doc_crud.get_document_by_id(db, id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    await doc_crud.delete_document(db, id)
    return {"status": "success", "message": "Document deleted successfully"}


# ---------------------------
# GET /{id}/download
# ---------------------------
@router.get("/{id}/download")
async def download_document(
    id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    """Download a document's original content."""
    doc = await doc_crud.get_document_by_id(db, id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    if not doc.meta_data or "text" not in doc.meta_data:
        raise HTTPException(status_code=400, detail="No content available for download")

    return Response(
        content=doc.meta_data["text"],
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={doc.filename}"},
    )
