# app/main.py

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import admin, auth, chat, documents, users, summarize, compare
from app.core.config import settings
from app.db.session import init_db
from app.core.startup import startup_tasks

app = FastAPI(
    title="GenAI Conversational Chatbot API",
    description="Backend API for the Conversational RAG Chat Application",
    root_path="/api",
    version="1.0.0",
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
# app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(summarize.router, prefix="/summarize", tags=["Summarization"])
app.include_router(compare.router, prefix="/compare", tags=["Compare"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.on_event("startup")
async def startup_event():
    MAX_RETRIES = 15

    for attempt in range(MAX_RETRIES):
        try:
            print(f"🔄 Initializing database (attempt {attempt+1}/{MAX_RETRIES})...")
            await init_db()
            print("✅ Database initialized successfully!")
            break
        except Exception as e:
            print(f"⏳ Database not ready yet: {e}")
            await asyncio.sleep(2)

    await startup_tasks()
    print("🚀 App started successfully!")


@app.get("/health", tags=["Health"])
async def root():
    return {"status": "ok", "message": "GenAI Chatbot API running 🚀"}
