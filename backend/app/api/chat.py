# app/api/chat.py

import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.crud import chat_crud
from app.db.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_pipeline import run_rag_pipeline
from app.core.security import get_current_user
from langchain_google_genai import ChatGoogleGenerativeAI

router = APIRouter()
from dotenv import load_dotenv
load_dotenv()

# Load Gemini API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not found in environment variables.")

# Initialize Gemini LLM via LangChain wrapper
gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=GEMINI_API_KEY,
    temperature=0.2,
)

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
        # Step 1: Get retrieved context + formulate the prompt
        llm_output, sources = await run_rag_pipeline(
            request.message, current_user.id, db, llm=gemini
        )

        # Step 2: Log chat message and assistant response
        await chat_crud.log_message(
            db,
            current_user.id,
            request.session_id,
            request.message,
            llm_output
        )

        # Step 3: Return chat response
        return ChatResponse(
            session_id=request.session_id,
            user_message=request.message,
            assistant_message=llm_output,
            sources=sources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {e}")