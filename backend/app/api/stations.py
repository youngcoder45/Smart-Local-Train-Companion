from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Query

from app.schemas.stations import Station

router = APIRouter(prefix="/api", tags=["stations"])


def _normalize(s: str) -> str:
    return " ".join(s.strip().lower().split())


def _data_path() -> Path:
    # backend/app/api/stations.py -> backend/
    return Path(__file__).resolve().parents[2]


def _load_stations() -> list[Station]:
    """
    Loads stations from `backend/data/stations.json`.

    Expected format (current repo):
      [
        {
          "id": "CSMT",
          "name": "Chhatrapati Shivaji Maharaj Terminus",
          "aliases": ["CSMT", "CST", "VT"],
          "line": ["Central", "Harbour"],
          "city": "Mumbai",
          "lat": 18.9402,
          "lon": 72.8356
        },
        ...
      ]

    We normalize to the shared API schema:
      Station(code=<id>, name=<name>, city=<city>, line=<first line as string>, lat, lon)
    """
    data_file = _data_path() / "data" / "stations.json"
    if not data_file.exists():
        # Fallback minimal list if data file is removed/missing
        return [
            Station(code="CSMT", name="Chhatrapati Shivaji Maharaj Terminus", city="Mumbai"),
            Station(code="DR", name="Dadar", city="Mumbai"),
            Station(code="BCT", name="Mumbai Central", city="Mumbai"),
            Station(code="ADH", name="Andheri", city="Mumbai"),
            Station(code="TNA", name="Thane", city="Thane"),
            Station(code="KYN", name="Kalyan Junction", city="Kalyan"),
            Station(code="PNVL", name="Panvel", city="Navi Mumbai"),
        ]

    raw: list[dict[str, Any]] = json.loads(data_file.read_text(encoding="utf-8"))
    out: list[Station] = []
    for item in raw:
        line_value: str | None = None
        if isinstance(item.get("line"), list) and item["line"]:
            # shared schema currently models `line` as a string; pick the first for MVP
            line_value = str(item["line"][0])

        out.append(
            Station(
                code=str(item.get("id") or item.get("code") or ""),
                name=str(item.get("name") or ""),
                city=item.get("city"),
                line=line_value,
                lat=item.get("lat"),
                lon=item.get("lon"),
            )
        )

    # Filter out any malformed entries
    out = [s for s in out if s.code and s.name]
    return out


@router.get("/stations", response_model=list[Station])
def list_stations(
    query: str = Query(
        default="",
        description="Search term (matches station name or code).",
        max_length=80,
    ),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[Station]:
    """
    Returns stations filtered by `query`.

    Frontend use-cases:
    - Autocomplete for source/destination
    - Validate station input (switch from free-text to selection later)
    """
    stations = _load_stations()

    q = _normalize(query)
    if not q:
        return stations[:limit]

    out: list[Station] = []
    for st in stations:
        # match by name/code (and allow code search even if user types partial)
        if q in _normalize(st.name) or q in _normalize(st.code):
            out.append(st)
        if len(out) >= limit:
            break
    return out
