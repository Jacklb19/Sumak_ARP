from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    Configuración global del backend
    """
    # SUPABASE
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # GROQ 
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-specdec"

    # JWT & SECURITY
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Backend
    BACKEND_URL: str = "http://localhost:8000"
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # N8N
    N8N_WEBHOOK_SECRET: str = ""

    # SENDGRID
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@techrecruiter.com"

    # LANGGRAPH
    LANGGRAPH_URL: str = "http://localhost:8001"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global
settings = Settings()