from fastapi import APIRouter, Response, UploadFile, File, Depends, HTTPException
import fitz
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.db.models import Document
from app.db.crud import doc_crud
from app.core.security import get_current_user
from app.core.config import settings

from app.processing.extract_content import extract_content
from app.services.document_service import process_and_store_document

from app.utils.async_minio import async_minio


router = APIRouter(tags=["Documents"])


# ===========================
# POST /upload
# ===========================
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        # Read only ONCE
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(400, "Empty file uploaded")

        # Upload to MinIO via async wrapper
        object_name = f"{current_user.id}/{file.filename}"
        minio_uri = await async_minio.upload_bytes(
            bucket=settings.MINIO_DOCUMENT_BUCKET,
            object_name=object_name,
            data=file_bytes,
            content_type=file.content_type,
        )

        # Extract content from bytes (not UploadFile)
        extracted = await extract_content(file_bytes, filename=file.filename)

        # Store in DB
        doc = await process_and_store_document(
            db=db,
            owner_id=current_user.id,
            filename=file.filename,
            content=extracted,
            content_type=file.content_type,   
            size=len(file_bytes),
            metadata={"minio_uri": minio_uri},
        )

        return {
            "success": True,
            "document": {
                "id": str(doc.id),
                "filename": doc.filename,
                "minio_uri": minio_uri,
                "size": doc.size,
                "uploaded_at": doc.uploaded_at,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


# ===========================
# GET /list
# ===========================
@router.get("/list")
async def list_documents(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    docs = await doc_crud.get_user_documents(db, user_id=current_user.id, limit=limit, offset=offset)

    return {
        "success": True,
        "data": [
            {
                "id": str(doc.id),
                "filename": doc.filename,
                "mimeType": doc.content_type,
                "uploadedAt": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                "summary": (doc.meta_data or {}).get("summary"),
                # "extractedText": (doc.meta_data or {}).get("text"),
                "status": "completed",  # customizable
                "downloadUrl": f"/api/documents/{doc.id}/download",
            }
            for doc in docs
        ],
    }


# ===========================
# GET /{id}
# ===========================
@router.get("/{id}")
async def get_document(
    id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    doc = await doc_crud.get_document_by_id(db, id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(404, "Document not found")

    return {
        "id": str(doc.id),
        "filename": doc.filename,
        "mimeType": doc.content_type,
        "uploadedAt": doc.uploaded_at,
        "metadata": doc.meta_data,
        "content": doc.content,
    }


# ===========================
# PUT /{id}
# ===========================
@router.put("/{id}")
async def update_document(
    id: UUID,
    metadata: dict,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    doc = await doc_crud.get_document_by_id(db, id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(404, "Document not found")

    updated = await doc_crud.update_document_metadata(db, id, metadata)
    return {"success": True, "updated": updated}


# ===========================
# DELETE /{id}
# ===========================
@router.delete("/{id}")
async def delete_document(
    id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    doc = await doc_crud.get_document_by_id(db, id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(404, "Document not found")

    await doc_crud.delete_document(db, id)
    return {"success": True, "message": "Document deleted successfully"}


# ===========================
# GET /{id}/download
# ===========================
@router.get("/{id}/download")
async def download_document(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    doc = await doc_crud.get_document_by_id(db, id)

    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(404, "Document not found")

    if not doc.meta_data:
        raise HTTPException(400, "Document missing metadata")

    minio_uri = doc.meta_data.get("minio_uri")
    if not minio_uri:
        raise HTTPException(400, "Document storage missing")

    bucket, object_name = minio_uri.split("/", 1)

    # Generate async presigned URL
    url = await async_minio.generate_presigned_url(bucket, object_name)
    if not url:
        raise HTTPException(500, "Failed generating download URL")

    return {
        "success": True,
        "downloadUrl": url,
        "filename": doc.filename,
    }


# ===========================
# GET /{id}/page/{page}/image
# ===========================
@router.get("/{id}/page/{page}/image")
async def get_pdf_page_image(
    id: UUID,
    page: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Returns a PDF page as an image (PNG). Useful for citation previews or rendering pages.
    """

    # 1️⃣ Validate document
    doc = await doc_crud.get_document_by_id(db, id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(404, "Document not found")

    if doc.content_type not in ("application/pdf", "pdf"):
        raise HTTPException(400, "Document is not a PDF")

    # 2️⃣ Get MinIO reference
    minio_uri = (doc.meta_data or {}).get("minio_uri")
    if not minio_uri:
        raise HTTPException(400, "Document storage reference missing")

    bucket, object_name = minio_uri.split("/", 1)

    # 3️⃣ Download file bytes from MinIO
    # pdf_bytes = await async_minio.get_object_bytes(bucket, object_name)
    pdf_bytes = await async_minio.download_bytes(bucket, object_name)

    if not pdf_bytes:
        raise HTTPException(500, "Failed retrieving document from storage")

    # 4️⃣ Open and render specific page
    try:
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Fix page indexing (API expects 1-based, PyMuPDF uses 0-based)
        page_index = page - 1

        if page_index < 0 or page_index >= len(pdf):
            raise HTTPException(400, f"Page {page} out of range. PDF has {len(pdf)} pages.")

        page_obj = pdf[page_index]
        pix = page_obj.get_pixmap(dpi=150)  # good quality

        img_bytes = pix.tobytes("png")

        return Response(content=img_bytes, media_type="image/png")

    except Exception as e:
        raise HTTPException(500, f"Failed to render page: {e}")
