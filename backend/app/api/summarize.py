from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.db.session import get_db
from app.core.security import get_current_user
from app.db.models import Document
from app.db.models import Summary
from app.db.schemas.summary import SummaryCreateRequest, SummaryResponse
from app.services.summarizer import generate_summary
from typing import List
import uuid

router = APIRouter(tags=["Summarization"])


# -------------------------
# 1. POST /api/summarize
# -------------------------
@router.post("", response_model=dict)
async def create_summary(
    req: SummaryCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    doc = await db.get(Document, req.documentId)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    # Simulate processing / summary generation
    processing = False  # Example toggle — replace with real async job logic

    summary_id = f"{uuid.uuid4()}"
    now = datetime.utcnow()

    if processing:
        return {
            "success": True,
            "data": {
                "summary": {
                    "id": summary_id,
                    "documentId": req.documentId,
                    "status": "processing",
                    "createdAt": now.isoformat() + "Z",
                    "estimatedCompletionTime": (now + timedelta(minutes=2)).isoformat() + "Z",
                    "message": "Summary is being generated. Use the summary ID to check status.",
                }
            },
        }

    summary_data = await generate_summary(req, current_user.id, doc)

    summary = Summary(
        id=summary_id,
        document_id=req.documentId,
        style=req.options.style,
        length=req.options.length,
        content=summary_data["content"],
        key_points=summary_data["keyPoints"],
        word_count=summary_data["wordCount"],
        confidence=summary_data["confidence"],
        created_at=now,
        meta_data=summary_data["meta_data"],
    )
    db.add(summary)
    await db.commit()

    return {"success": True, "data": {"summary": SummaryResponse.from_orm(summary)}}


# -------------------------
# 2. GET /api/summarize/:documentId
# -------------------------
@router.get("/{document_id}", response_model=dict)
async def get_summaries(
    document_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    from sqlalchemy import select

    result = await db.execute(select(Summary).where(Summary.document_id == document_id))
    summaries = result.scalars().all()

    if not summaries:
        raise HTTPException(status_code=404, detail="No summaries found for this document")

    return {"success": True, "data": {"summaries": summaries}}


# -------------------------
# 3. GET /api/summarize/summary/:summaryId
# -------------------------
@router.get("/summary/{summary_id}", response_model=dict)
async def get_summary(
    summary_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    summary = await db.get(Summary, summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    return {"success": True, "data": {"summary": summary}}


# -------------------------
# 4. DELETE /api/summarize/:summaryId
# -------------------------
@router.delete("/{summary_id}", response_model=dict)
async def delete_summary(
    summary_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    summary = await db.get(Summary, summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    await db.delete(summary)
    await db.commit()
    return {
        "success": True,
        "data": {"message": "Summary deleted successfully", "summaryId": summary_id},
    }


# -------------------------
# 5. POST /api/summarize/batch
# -------------------------
@router.post("/batch", response_model=dict)
async def batch_summarize(
    req: dict, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    now = datetime.utcnow()
    batch_id = f"batch_{uuid.uuid4().hex[:10]}"
    docs = req.get("documentIds", [])
    summaries = []

    for i, doc_id in enumerate(docs):
        summaries.append(
            {
                "documentId": doc_id,
                "status": "queued",
                "estimatedCompletionTime": (now + timedelta(minutes=i + 2)).isoformat() + "Z",
            }
        )

    return {
        "success": True,
        "data": {
            "batchId": batch_id,
            "summaries": summaries,
            "message": "Batch summarization initiated. Check individual document summaries for updates.",
        },
    }


# -------------------------
# 6. POST /api/summarize/custom
# -------------------------
@router.post("/custom", response_model=dict)
async def custom_summary(
    req: dict, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    doc = await db.get(Document, req.get("documentId"))
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    summary_data = await generate_summary(req, current_user.id, doc, custom=True)
    summary_id = f"sum_{uuid.uuid4().hex[:10]}"

    summary = Summary(
        id=summary_id,
        document_id=req["documentId"],
        style="custom",
        content=summary_data["content"],
        key_points=summary_data.get("keyPoints", []),
        word_count=summary_data.get("wordCount"),
        confidence=summary_data.get("confidence"),
        created_at=datetime.utcnow(),
        meta_data=summary_data.get("meta_data", {}),
    )
    db.add(summary)
    await db.commit()

    return {"success": True, "data": {"summary": SummaryResponse.from_orm(summary)}}
