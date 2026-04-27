from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized configuration for the FastAPI backend.

    Values are loaded from environment variables and (optionally) a `.env` file.
    Environment variables take precedence over `.env`.

    Typical usage:
        from app.core.settings import get_settings
        settings = get_settings()
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Project
    APP_NAME: str = "SLTM Backend"
    ENV: str = "development"  # development | staging | production
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    # For local dev with Vite (default port 5173)
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # API
    API_V1_PREFIX: str = "/api"

    # Data / persistence (optional for MVP)
    DATABASE_URL: str | None = None

    # External integrations (placeholders for later)
    # Example: TRAIN_TIMINGS_API_KEY, MAPBOX_TOKEN, etc.
    TRAIN_TIMINGS_API_KEY: str | None = None

    @property
    def is_production(self) -> bool:
        return self.ENV.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.ENV.lower() == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Cached settings instance (safe to import across the app).
    """
    return Settings()
