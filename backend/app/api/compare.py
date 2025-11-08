import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.session import get_db
from app.db.models import Document
from app.core.security import get_current_user
from app.services.compare_service import compare_documents
from app.services.compare_service import run_document_comparison
from app.db.crud import compare_crud
from app.db.models import Comparison  # assuming you’ll add this model
from app.db.schemas.compare import (
    CompareHistoryResponse,
    CompareDetailResponse,
    CompareDeleteResponse,
    CompareBatchRequest,
    CompareBatchResponse,
    ComparisonRequest
)

router = APIRouter(tags=["Compare"])


# ===========================================================
# 1. POST /api/compare
# ===========================================================

@router.post("")
async def compare_documents_api(
    request: ComparisonRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Fetch both documents
    doc1 = await db.get(Document, request.documentId1)
    doc2 = await db.get(Document, request.documentId2)
    if not doc1 or not doc2:
        raise HTTPException(status_code=404, detail="One or both documents not found")

    # Run comparison
    result = await run_document_comparison(doc1, doc2, request.comparisonType, request.options.dict())

    # Persist
    comparison = await compare_crud.create_comparison(
        db,
        current_user.id,
        doc1.id,
        doc2.id,
        request.comparisonType,
        meta_data=result
    )

    return {"success": True, "data": {"comparison": result}}


# ===========================================================
# 2. GET /api/compare/{id}
# ===========================================================
@router.get("/{id}", response_model=CompareDetailResponse)
async def get_comparison_result(
    id: uuid.UUID,
    includeDetails: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get comparison results by ID.
    """
    q = select(Comparison).where(Comparison.id == id, Comparison.user_id == current_user.id)
    res = await db.execute(q)
    cmp = res.scalars().first()
    if not cmp:
        raise HTTPException(status_code=404, detail="Comparison not found")

    return {"success": True, "data": {"comparison": cmp.to_dict(includeDetails)}}


# ===========================================================
# 3. GET /api/compare/history
# ===========================================================
@router.get("/history", response_model=CompareHistoryResponse)
async def get_comparison_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    documentId: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get comparison history for the current user.
    """
    query = select(Comparison).where(Comparison.user_id == current_user.id)
    if documentId:
        query = query.where(
            (Comparison.document_id1 == documentId) | (Comparison.document_id2 == documentId)
        )
    result = await db.execute(query.order_by(Comparison.created_at.desc()))
    comparisons = result.scalars().all()

    total_items = len(comparisons)
    total_pages = (total_items + limit - 1) // limit
    start = (page - 1) * limit
    paginated = comparisons[start : start + limit]

    return {
        "success": True,
        "data": {
            "comparisons": [cmp.to_summary() for cmp in paginated],
            "pagination": {
                "currentPage": page,
                "totalPages": total_pages,
                "totalItems": total_items,
            },
        },
    }


# ===========================================================
# 4. DELETE /api/compare/{id}
# ===========================================================
@router.delete("/{id}", response_model=CompareDeleteResponse)
async def delete_comparison(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Delete a comparison result.
    """
    q = select(Comparison).where(Comparison.id == id, Comparison.user_id == current_user.id)
    res = await db.execute(q)
    cmp = res.scalars().first()
    if not cmp:
        raise HTTPException(status_code=404, detail="Comparison not found")

    await db.delete(cmp)
    await db.commit()

    return {"success": True, "data": {"message": "Comparison deleted successfully", "comparisonId": str(id)}}


# ===========================================================
# 5. POST /api/compare/batch
# ===========================================================
@router.post("/batch", response_model=CompareBatchResponse)
async def batch_compare_documents(
    request: CompareBatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Compare multiple document pairs in batch mode.
    """
    comparisons = []
    batch_id = f"batch_{uuid.uuid4().hex[:10]}"
    for cmp_req in request.comparisons:
        cmp_id = f"cmp_{uuid.uuid4().hex[:10]}"
        comparisons.append({
            "id": cmp_id,
            "status": "queued"
        })

    return {
        "success": True,
        "data": {
            "batchId": batch_id,
            "comparisons": comparisons,
            "message": "Batch comparison initiated. Check status for updates."
        },
    }
