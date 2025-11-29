"""Application settings and configuration."""

from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8001, ge=1024, le=65535, description="API port")
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Environment"
    )

    # Google Gemini Configuration (CORREGIDO)
    google_api_key: str = Field(..., description="Google AI Studio API key")
    gemini_model: str = Field(default="gemini-2.0-flash", description="Gemini model")
    gemini_temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Temperature")
    gemini_max_tokens: int = Field(default=500, ge=1, le=8000, description="Max output tokens")

    # Supabase Configuration
    supabase_url: str = Field(..., description="Supabase URL")
    supabase_key: str = Field(..., description="Supabase anon key")

    # Backend Service
    backend_url: str = Field(default="http://localhost:8000", description="Backend URL")
    backend_timeout: int = Field(default=30, ge=5, le=120, description="Backend timeout")

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Log level"
    )
    log_format: Literal["json", "text"] = Field(default="json", description="Log format")

    # Interview Configuration
    max_knockout_questions: int = Field(default=3, ge=1, le=10)
    max_technical_questions: int = Field(default=5, ge=1, le=15)
    max_soft_skills_questions: int = Field(default=3, ge=1, le=10)
    cv_context_length: int = Field(default=1000, ge=100, le=5000)

    @field_validator("supabase_url", "backend_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v.rstrip("/")

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"


settings = Settings()
