# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import admin, auth, chat, documents, users, summarize, compare
from app.core.config import settings
from app.db.session import init_db

app = FastAPI(
    title="GenAI Conversational Chatbot API",
    description="Backend API for the Conversational RAG Chat Application",
    root_path="/api",
    version="1.0.0"
)

# ✅ CORS setup for frontend (React/Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include API routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(summarize.router, prefix="/summarize", tags=["Summarization"])
app.include_router(compare.router, prefix="/compare", tags=["Compare"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

@app.on_event("startup")
async def startup_event():
    await init_db()
    print("✅ Database initialized and app started successfully!")

@app.get("/health", tags=["Health"])
async def root():
    return {"status": "ok", "message": "GenAI Chatbot API running 🚀"}
