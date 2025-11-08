# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    APP_NAME: str = "GenAI Chatbot"
    DEBUG: bool = True

    # DB
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/genai_db"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # JWT
    SECRET_KEY: str = "CHANGE_ME_TO_A_SECURE_RANDOM_STRING"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI or LLM provider keys
    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    VECTOR_DB_PATH: str = "./app/data/faiss_index"

    # ✅ Add Qdrant
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "documents")


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"   

settings = Settings()
