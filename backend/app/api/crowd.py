from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["crowd"])


# -----------------------------
# Schemas
# -----------------------------
CrowdCategory = Literal["LOW", "MEDIUM", "HIGH", "SEVERE"]


class CrowdCoach(BaseModel):
    coach: str = Field(..., description="Coach identifier (e.g., C1, C2, ...)")
    crowd_score: int = Field(..., ge=0, le=100, description="0..100 crowd score")
    category: CrowdCategory = Field(..., description="Bucketed crowd level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence 0..1")


class CrowdPredictionResponse(BaseModel):
    train_id: str
    source: str
    destination: str
    as_of: datetime
    factors: list[str]
    coaches: list[CrowdCoach]


class BestCoachRecommendationResponse(BaseModel):
    train_id: str
    destination: str
    as_of: datetime
    recommended: list[str] = Field(..., description="Ordered list of best coaches to board")
    reasoning: list[str]
    coaches: list[CrowdCoach]


# -----------------------------
# Tiny rule-based "prediction"
# (MVP placeholder; swap with ML later)
# -----------------------------
def _peak_multiplier(dt: datetime) -> float:
    hour = dt.hour
    # Mumbai-ish: morning/evening peaks
    if 8 <= hour <= 11 or 18 <= hour <= 21:
        return 1.25
    if 12 <= hour <= 17:
        return 0.95
    return 1.05


def _weekday_multiplier(dt: datetime) -> float:
    # 0=Mon ... 6=Sun
    if dt.weekday() <= 4:
        return 1.15
    return 0.9


def _category(score: int) -> CrowdCategory:
    if score < 30:
        return "LOW"
    if score < 55:
        return "MEDIUM"
    if score < 75:
        return "HIGH"
    return "SEVERE"


def _clamp_int(v: float, lo: int = 0, hi: int = 100) -> int:
    return int(max(lo, min(hi, round(v))))


def _coach_ids(num_coaches: int) -> list[str]:
    return [f"C{i}" for i in range(1, num_coaches + 1)]


def _baseline_profile(num_coaches: int) -> list[int]:
    """
    Simple convex profile: middle coaches tend to be more crowded.
    Produces scores roughly between ~35..70 before multipliers.
    """
    mid = (num_coaches + 1) / 2.0
    out: list[int] = []
    for i in range(1, num_coaches + 1):
        dist = abs(i - mid) / mid  # 0..~1
        score = 70 - (dist * 35)  # middle ~70, edges ~35
        out.append(_clamp_int(score))
    return out


def _predict_coaches(
    *,
    train_id: str,
    source: str,
    destination: str,
    dt: datetime,
    num_coaches: int,
) -> tuple[list[CrowdCoach], list[str]]:
    factors: list[str] = []
    pm = _peak_multiplier(dt)
    wm = _weekday_multiplier(dt)

    if pm > 1.1:
        factors.append("Peak-hour multiplier applied")
    else:
        factors.append("Off-peak multiplier applied")

    if wm > 1.0:
        factors.append("Weekday multiplier applied")
    else:
        factors.append("Weekend multiplier applied")

    base = _baseline_profile(num_coaches)

    coaches: list[CrowdCoach] = []
    for coach, base_score in zip(_coach_ids(num_coaches), base, strict=False):
        score = _clamp_int(base_score * pm * wm)

        # Confidence is intentionally conservative as this is rule-based.
        # You can increase confidence later when you add real sampling + model.
        confidence = 0.55
        coaches.append(
            CrowdCoach(
                coach=coach,
                crowd_score=score,
                category=_category(score),
                confidence=confidence,
            )
        )

    return coaches, factors


def _recommend_best_coaches(coaches: list[CrowdCoach], k: int) -> list[str]:
    """
    MVP heuristic:
      Prefer lowest crowd_score.
      Break ties by coach id (stable).
    """
    ordered = sorted(coaches, key=lambda c: (c.crowd_score, c.coach))
    return [c.coach for c in ordered[:k]]


# -----------------------------
# Routes
# -----------------------------
@router.get("/crowd", response_model=CrowdPredictionResponse)
def predict_crowd(
    train_id: str = Query(..., min_length=1),
    source: str = Query(..., min_length=1),
    destination: str = Query(..., min_length=1),
    num_coaches: int = Query(12, ge=6, le=24, description="Typical local: 12 or 15"),
    at: datetime | None = Query(
        None,
        description="Timestamp for prediction; defaults to now (UTC). "
        "If you send a naive datetime, it's treated as UTC.",
    ),
):
    """
    Returns a rule-based crowd estimate per coach.

    Notes:
    - This is an MVP placeholder meant to unblock frontend heatmap UI.
    - Replace internals with real-time feeds + historical/ML later.
    """
    dt = at or datetime.now(UTC)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    coaches, factors = _predict_coaches(
        train_id=train_id,
        source=source,
        destination=destination,
        dt=dt,
        num_coaches=num_coaches,
    )

    return CrowdPredictionResponse(
        train_id=train_id,
        source=source,
        destination=destination,
        as_of=dt,
        factors=factors,
        coaches=coaches,
    )


@router.get("/recommend/best-coach", response_model=BestCoachRecommendationResponse)
def recommend_best_coach(
    train_id: str = Query(..., min_length=1),
    destination: str = Query(..., min_length=1),
    source: str = Query("", description="Optional; used for future refinements"),
    k: int = Query(2, ge=1, le=5, description="How many coach options to return"),
    num_coaches: int = Query(12, ge=6, le=24),
    at: datetime | None = Query(None, description="Timestamp; defaults to now (UTC)"),
):
    """
    Returns recommended coach(es) based on lowest predicted crowd.

    Future evolution:
    - Incorporate station exit mapping (best coach for fastest exit)
    - Incorporate directionality, interchange congestion, platform exits
    - Blend live data (scrape/API) with historical baseline
    """
    dt = at or datetime.now(UTC)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    coaches, factors = _predict_coaches(
        train_id=train_id,
        source=source or "UNKNOWN",
        destination=destination,
        dt=dt,
        num_coaches=num_coaches,
    )

    recommended = _recommend_best_coaches(coaches, k=k)

    reasoning: list[str] = [
        "Recommendation is based on lowest predicted crowd per coach (rule-based MVP).",
        *factors,
        "This endpoint will later incorporate station exits to optimize for fastest exit at destination.",
    ]

    return BestCoachRecommendationResponse(
        train_id=train_id,
        destination=destination,
        as_of=dt,
        recommended=recommended,
        reasoning=reasoning,
        coaches=coaches,
    )
