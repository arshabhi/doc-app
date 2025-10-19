# app/api/chat.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.crud import chat_crud
from app.db.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_pipeline import run_rag_pipeline
from app.core.security import get_current_user

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Handles a new chat message with retrieval-augmented generation.
    """
    try:
        # Call RAG pipeline (LLM + vector search)
        llm_output, sources = await run_rag_pipeline(request.message, current_user.id, db)

        # Store message and response in chat history
        await chat_crud.log_message(db, current_user.id, request.session_id, request.message, llm_output)

        return ChatResponse(
            session_id=request.session_id,
            user_message=request.message,
            assistant_message=llm_output,
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {e}")
