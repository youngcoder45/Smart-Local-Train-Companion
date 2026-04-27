# SLTM Backend (FastAPI)

This folder contains the **FastAPI** backend for the SLTM project (Smart Local Train Companion).

It is currently an **MVP backend** designed to unblock frontend development by providing stable APIs with **mock / rule-based** data:
- Station search (`/api/stations`)
- Journey options (`/api/journeys`)
- Train timings (mock) (`/api/timings`)
- Crowd heatmap prediction (rule-based) (`/api/crowd`)
- Best coach recommendation (rule-based) (`/api/recommend/best-coach`)
- Health check (`/health`)

---

## Repo structure (backend)

```SLTM/backend/README.md#L20-36
backend/
  app/
    main.py              # FastAPI app + CORS + router registration
    api/                 # API endpoints (routers)
      health.py
      stations.py
      journeys.py
      crowd.py
    schemas/             # Pydantic schemas (shared models)
    core/
      settings.py        # env/.env configuration (optional)
  data/
    stations.json        # basic Mumbai-focused station dataset
  pyproject.toml         # Python deps (PEP 621)
  .env.example           # environment example (copy to .env)
```

---

## Requirements

- Python **3.11+**
- pip (or uv/poetry if you want, but pip is enough)

---

## Setup (recommended: virtual environment)

From the repository root:

```SLTM/backend/README.md#L42-56
cd backend
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows (PowerShell)
# .venv\Scripts\Activate.ps1
```

Upgrade pip:

```SLTM/backend/README.md#L58-61
python -m pip install --upgrade pip
```

Install dependencies:

```SLTM/backend/README.md#L63-68
# Install runtime deps (FastAPI, uvicorn, etc.)
pip install -e .

# Optionally install dev deps (pytest, ruff, etc.)
# pip install -e ".[dev]"
```

---

## Environment configuration

Copy the example env file:

```SLTM/backend/README.md#L72-76
cp .env.example .env
```

Common values:
- `PORT=8000`
- `CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173` (Vite dev server)

> Never commit `.env`.

---

## Run the API server (development)

From `backend/`:

```SLTM/backend/README.md#L83-86
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

---

## CORS (frontend integration)

The backend enables CORS for typical local dev origins, including:
- `http://localhost:5173` (Vite default)
- `http://127.0.0.1:5173`

So your frontend can call APIs like:
- `GET http://localhost:8000/api/stations?query=dadar`
- `GET http://localhost:8000/api/journeys?source=Andheri&destination=Dadar`

---

## API Endpoints (MVP)

### Health
- `GET /health`

### Stations
- `GET /api/stations?query=<text>&limit=20`

This reads from `data/stations.json` (Mumbai-focused) and returns matching stations.

### Journeys (mock routes)
- `GET /api/journeys?source=<source>&destination=<dest>`

Returns mock journey options so frontend can build the journey list UI.

### Timings (mock schedules)
- `GET /api/timings?source=<source>&destination=<dest>&when=<iso-datetime>`

Example:
- `/api/timings?source=Andheri&destination=Dadar&when=2026-04-27T10:30:00+05:30`

### Crowd prediction (rule-based)
- `GET /api/crowd?train_id=<id>&source=<source>&destination=<dest>&num_coaches=12&at=<iso-datetime>`

### Best coach recommendation (rule-based)
- `GET /api/recommend/best-coach?train_id=<id>&destination=<dest>&k=2&num_coaches=12&at=<iso-datetime>`

---

## Data: stations list

Stations are defined in:

- `data/stations.json`

You can safely expand this dataset (add more stations/aliases/lines/coordinates).
The API currently normalizes this into a simpler shape for the frontend.

---

## Next steps (planned upgrades)

This backend is intentionally simple. Likely next milestones:

1. **Real train timings**
   - Add provider abstraction (API + scrape hybrid)
   - Add caching (to avoid hammering sources)
2. **Persistent DB (PostgreSQL)**
   - Bookmarks, user preferences, historical crowd observations
3. **Crowd prediction v2**
   - Store observations + model training later
   - Move from rule-based to ML/hybrid
4. **Best-coach-for-exit**
   - Add station exit metadata and platform mapping

---

## Troubleshooting

### `ModuleNotFoundError: app`
Make sure you run `uvicorn` **from inside** the `backend/` directory:

```SLTM/backend/README.md#L159-162
cd backend
uvicorn app.main:app --reload
```

### Frontend can’t call backend (CORS)
- Confirm backend is running on `http://localhost:8000`
- Confirm frontend is on `http://localhost:5173`
- If your origin differs, add it to CORS configuration (in `app/main.py`) or via env-supported settings (future improvement).

---