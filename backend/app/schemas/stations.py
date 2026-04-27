from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Station(BaseModel):
    """
    Canonical station representation used across the API.

    Notes:
    - `code` can be a short station code (if you have one) or a stable slug.
    - Keep `name` human-readable (e.g., "Andheri").
    """

    code: str = Field(
        ..., min_length=1, max_length=32, description="Stable station code/slug"
    )
    name: str = Field(
        ..., min_length=1, max_length=128, description="Display name of the station"
    )

    # Optional metadata (helpful later for maps / ranking / filtering)
    city: Optional[str] = Field(
        default=None, max_length=64, description="City (e.g., Mumbai)"
    )
    line: Optional[str] = Field(
        default=None, max_length=64, description="Line/corridor (e.g., Western)"
    )
    lat: Optional[float] = Field(default=None, ge=-90, le=90, description="Latitude")
    lon: Optional[float] = Field(default=None, ge=-180, le=180, description="Longitude")


class StationSearchResponse(BaseModel):
    query: str = Field(..., description="Original search query")
    results: List[Station] = Field(
        default_factory=list, description="Matching stations"
    )


class StationListResponse(BaseModel):
    results: List[Station] = Field(
        default_factory=list, description="All stations (optionally filtered)"
    )
