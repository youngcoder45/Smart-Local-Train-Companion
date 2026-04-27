from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Register only routers that exist in `app/api/`.
# Keeping these imports explicit prevents startup errors when modules are removed/renamed.
from app.api.crowd import router as crowd_router
from app.api.health import router as health_router
from app.api.journeys import router as journeys_router
from app.api.stations import router as stations_router


def create_app() -> FastAPI:
    """
    FastAPI application factory.

    - Enables CORS for the Vite dev server (default: http://localhost:5173)
    - Registers API routers (health, stations, journeys/timings, crowd/recommendations)
    """
    app = FastAPI(
        title="SLTM Backend",
        version="0.1.0",
        description="Backend API for the Smart Local Train Companion (Mumbai-focused).",
    )

    # CORS: allow the React dev server and typical local origins.
    # You can tighten this list later for production.
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Root endpoint (handy for quick sanity checks)
    @app.get("/", tags=["meta"])
    def root() -> dict:
        return {
            "name": "SLTM Backend",
            "status": "ok",
            "docs": "/docs",
            "redoc": "/redoc",
        }

    # Register routers
    app.include_router(health_router)
    app.include_router(stations_router)
    app.include_router(journeys_router)
    app.include_router(crowd_router)

    return app


app = create_app()
