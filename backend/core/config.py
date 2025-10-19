# app/core/config.py
from pydantic import BaseSettings, AnyUrl
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "GenAI Chatbot"
    DEBUG: bool = True

    # DB
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/genai_db"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # JWT
    SECRET_KEY: str = "CHANGE_ME_TO_A_SECURE_RANDOM_STRING"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI or LLM provider keys
    OPENAI_API_KEY: str = ""

    VECTOR_DB_PATH: str = "./app/data/faiss_index"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
