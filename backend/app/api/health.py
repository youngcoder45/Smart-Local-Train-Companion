from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    service: str = Field(..., examples=["sltm-backend"])
    time_utc: datetime


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """
    Simple health check endpoint.

    Use-cases:
    - Verify the backend is running (for local dev and CI)
    - Basic uptime checks

    Returns current UTC time to help detect clock/process issues.
    """
    return HealthResponse(
        status="ok",
        service="sltm-backend",
        time_utc=datetime.now(UTC),
    )
