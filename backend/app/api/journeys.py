from __future__ import annotations

from datetime import UTC, datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["journeys"])


# -----------------------------
# Schemas
# -----------------------------


class JourneyLeg(BaseModel):
    mode: str = Field(..., description="E.g. 'TRAIN', 'WALK', 'METRO'")
    from_station: str = Field(..., description="Station code or human-readable name")
    to_station: str = Field(..., description="Station code or human-readable name")
    line: Optional[str] = Field(None, description="E.g. 'Western', 'Central', etc.")
    duration_minutes: Optional[int] = Field(
        None, description="Estimated duration in minutes for this leg"
    )


class JourneyOption(BaseModel):
    journey_id: str
    title: str
    legs: list[JourneyLeg]
    total_duration_minutes: int | None = None
    interchange_count: int = 0
    notes: list[str] = Field(default_factory=list)


class JourneysResponse(BaseModel):
    source: str
    destination: str
    options: list[JourneyOption]
    generated_at: datetime


class TrainTiming(BaseModel):
    train_id: str
    train_no: Optional[str] = None
    train_name: Optional[str] = None

    from_station: str
    to_station: str

    scheduled_departure: datetime
    expected_departure: datetime
    scheduled_arrival: Optional[datetime] = None
    expected_arrival: Optional[datetime] = None

    delay_minutes: int = 0
    platform: Optional[str] = None
    status: str = Field("ON_TIME", description="ON_TIME | DELAYED | CANCELLED | UNKNOWN")


class TimingsResponse(BaseModel):
    source: str
    destination: str
    when: datetime
    trains: list[TrainTiming]
    generated_at: datetime


# -----------------------------
# Helpers (mock data for MVP)
# -----------------------------


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _parse_when(when: str | None) -> datetime:
    """
    Accepts ISO-8601 with timezone (recommended) or any datetime string parseable by datetime.fromisoformat.
    Fallbacks to current UTC time.
    """
    if not when:
        return _now_utc()

    # Support "Z" suffix
    w = when.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(w)
    except ValueError:
        return _now_utc()

    if dt.tzinfo is None:
        # Treat naive timestamps as UTC to avoid confusion
        dt = dt.replace(tzinfo=UTC)
    return dt


def _mock_journey_options(source: str, destination: str) -> list[JourneyOption]:
    # Very simple placeholder: one direct train leg + optional interchange example.
    direct = JourneyOption(
        journey_id=str(uuid4()),
        title="Direct (suggested)",
        legs=[
            JourneyLeg(
                mode="TRAIN",
                from_station=source,
                to_station=destination,
                line=None,
                duration_minutes=45,
            )
        ],
        total_duration_minutes=45,
        interchange_count=0,
        notes=["This is a placeholder route (MVP)."],
    )

    interchange = JourneyOption(
        journey_id=str(uuid4()),
        title="1 Interchange (alternative)",
        legs=[
            JourneyLeg(
                mode="TRAIN",
                from_station=source,
                to_station=f"{source}-JUNCTION",
                line=None,
                duration_minutes=25,
            ),
            JourneyLeg(
                mode="WALK",
                from_station=f"{source}-JUNCTION",
                to_station=f"{source}-JUNCTION (platform change)",
                line=None,
                duration_minutes=5,
            ),
            JourneyLeg(
                mode="TRAIN",
                from_station=f"{source}-JUNCTION",
                to_station=destination,
                line=None,
                duration_minutes=30,
            ),
        ],
        total_duration_minutes=60,
        interchange_count=1,
        notes=["Alternate option if direct trains are crowded/delayed."],
    )

    return [direct, interchange]


def _mock_timings(source: str, destination: str, when_dt: datetime) -> list[TrainTiming]:
    # Generate a few trains at 10 minute intervals.
    base = when_dt.replace(second=0, microsecond=0)
    trains: list[TrainTiming] = []

    for i in range(5):
        scheduled_departure = base
        expected_departure = base

        # simulate some delay patterns
        delay = 0
        status = "ON_TIME"
        if i == 2:
            delay = 6
            status = "DELAYED"
            expected_departure = scheduled_departure.replace(minute=scheduled_departure.minute) + (
                expected_departure - scheduled_departure
            )

        # safer: just add timedelta
        # but to avoid importing timedelta unnecessarily in this file, keep simple:
        # We'll compute expected times using epoch math with datetime + seconds.
        from datetime import timedelta  # local import

        scheduled_departure = base + timedelta(minutes=10 * i)
        expected_departure = scheduled_departure + timedelta(minutes=delay)

        scheduled_arrival = scheduled_departure + timedelta(minutes=45)
        expected_arrival = scheduled_arrival + timedelta(minutes=delay)

        trains.append(
            TrainTiming(
                train_id=f"local-{i + 1}",
                train_no=str(90000 + i),
                train_name="Mumbai Local (Mock)",
                from_station=source,
                to_station=destination,
                scheduled_departure=scheduled_departure,
                expected_departure=expected_departure,
                scheduled_arrival=scheduled_arrival,
                expected_arrival=expected_arrival,
                delay_minutes=delay,
                platform=str((i % 6) + 1),
                status=status,
            )
        )

    return trains


# -----------------------------
# Routes
# -----------------------------


@router.get("/journeys", response_model=JourneysResponse)
def get_journeys(
    source: str = Query(..., min_length=1, description="Source station/name"),
    destination: str = Query(..., min_length=1, description="Destination station/name"),
) -> JourneysResponse:
    """
    Returns journey options from source -> destination.

    MVP behavior:
    - Returns mock journey options so the frontend can proceed.
    - Later replace with real routing logic (graph + GTFS + interchange rules).
    """
    return JourneysResponse(
        source=source,
        destination=destination,
        options=_mock_journey_options(source, destination),
        generated_at=_now_utc(),
    )


@router.get("/timings", response_model=TimingsResponse)
def get_timings(
    source: str = Query(..., min_length=1, description="Source station/name"),
    destination: str = Query(..., min_length=1, description="Destination station/name"),
    when: Optional[str] = Query(
        None,
        description="ISO datetime (e.g. 2026-04-27T10:30:00+05:30). Defaults to now (UTC).",
    ),
) -> TimingsResponse:
    """
    Returns train timings between source and destination around the given time.

    MVP behavior:
    - Returns mock timings at 10-minute intervals.
    - Later integrate scraped+API hybrid live timings and add caching.
    """
    when_dt = _parse_when(when)
    return TimingsResponse(
        source=source,
        destination=destination,
        when=when_dt,
        trains=_mock_timings(source, destination, when_dt),
        generated_at=_now_utc(),
    )
