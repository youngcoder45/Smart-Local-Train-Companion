from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CrowdLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class CoachType(str, Enum):
    GENERAL = "GENERAL"
    LADIES = "LADIES"
    FIRST_CLASS = "FIRST_CLASS"
    HANDICAP = "HANDICAP"
    UNKNOWN = "UNKNOWN"


class StationRef(BaseModel):
    """
    A lightweight station reference suitable for APIs.
    You can expand later with station codes, geo coords, line, etc.
    """

    name: str = Field(..., min_length=1, examples=["Andheri"])
    code: str | None = Field(default=None, examples=["ADH"])


class TrainRef(BaseModel):
    """
    A lightweight train reference suitable for listings.
    """

    train_id: str = Field(..., min_length=1, examples=["WR-FAST-1234"])
    name: str | None = Field(default=None, examples=["Virar Fast"])
    line: str | None = Field(default=None, examples=["Western"])
    direction: str | None = Field(default=None, examples=["UP", "DOWN"])


class TrainTiming(BaseModel):
    """
    A single timing record for a train between a source and destination.
    """

    train: TrainRef
    source: StationRef
    destination: StationRef

    scheduled_departure: datetime | None = Field(
        default=None, description="Scheduled departure time from source (local time)."
    )
    expected_departure: datetime | None = Field(
        default=None,
        description="Expected/estimated departure time from source (local time).",
    )
    scheduled_arrival: datetime | None = Field(
        default=None, description="Scheduled arrival time at destination (local time)."
    )
    expected_arrival: datetime | None = Field(
        default=None,
        description="Expected/estimated arrival time at destination (local time).",
    )

    delay_minutes: int | None = Field(
        default=None, description="Positive minutes of delay compared to schedule."
    )
    platform: str | None = Field(default=None, examples=["3"])
    status: str | None = Field(default=None, examples=["ON_TIME", "DELAYED", "CANCELLED"])
    last_updated: datetime | None = Field(default=None)


class CoachCrowd(BaseModel):
    """
    Crowd estimate for a specific coach/compartment.
    """

    coach_id: str = Field(..., min_length=1, examples=["C1", "C2", "L1"])
    coach_type: CoachType = Field(default=CoachType.UNKNOWN)
    crowd_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Crowd score 0-100 (higher means more crowded).",
        examples=[15, 55, 92],
    )
    level: CrowdLevel = Field(default=CrowdLevel.UNKNOWN)
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence in the estimate [0.0 - 1.0].",
        examples=[0.3, 0.7, 0.9],
    )


class CrowdHeatmapResponse(BaseModel):
    """
    Response payload for crowd heatmap.
    """

    train: TrainRef
    source: StationRef
    destination: StationRef
    at_time: datetime = Field(..., description="Time the crowd estimate applies to (local time).")

    coaches: list[CoachCrowd] = Field(default_factory=list)
    recommended_coaches: list[str] = Field(
        default_factory=list,
        description="Coach IDs recommended for boarding (e.g. least crowded / best exit).",
        examples=[["C10", "C11"]],
    )

    methodology: str | None = Field(
        default="rule-based",
        description="How this estimate was generated (e.g., rule-based, ML, hybrid).",
    )
    last_updated: datetime | None = None


class BestCoachRecommendation(BaseModel):
    """
    Recommendation for which coach to board for fastest exit / best experience.
    """

    train: TrainRef
    destination: StationRef
    reason: str = Field(..., min_length=1, examples=["Closest to main stairs/exit at destination"])
    recommended_coaches: list[str] = Field(
        ...,
        description="Coach IDs recommended for boarding (e.g. for least crowd / fastest exit).",
        examples=[["C3", "C4"]],
    )

    exit_hint: str | None = Field(
        default=None,
        description="Extra hint about where to stand/exit at destination (if known).",
        examples=["Use north stairway near platform entrance"],
    )
    last_updated: datetime | None = None
