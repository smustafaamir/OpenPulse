![OpenPulse banner](docs/banner.png)

# OpenPulse

Open-source, multi-tenant event intelligence platform. Every data source, dashboard, and integration communicates through a unified event model.

**v0.1 (MVP)** includes a FastAPI backend, React frontend, mock event collector, JWT auth, REST + WebSocket APIs, and Docker Compose for one-command local development.

## What's included

| Area | Status |
|------|--------|
| User registration, login, JWT refresh | Done |
| Multi-tenant organizations | Done |
| Event ingest, query, and tenant isolation | Done |
| Mock collector (~1 event/sec per organization) | Done |
| Live event stream via WebSocket | Done |
| Dashboard CRUD (create, list, get, update layout) | Done |
| React UI: Login, Dashboard, Events, Settings | Done |
| API key management | Deferred to v0.2 (schema exists) |

### Frontend pages

| Route | Description |
|-------|-------------|
| `/login` | Register or sign in |
| `/dashboard` | Live event feed, price chart, statistics, WebSocket status |
| `/events` | Historical events with filters and pagination |
| `/settings` | Organization details |

### Tech stack

| Layer | Technologies |
|-------|--------------|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, asyncpg, Redis |
| Frontend | React 18, TypeScript, Vite, TanStack Query, Zustand, Tailwind CSS, Recharts |
| Infrastructure | PostgreSQL 15, Redis 7, Docker Compose |

## Repository layout

```
MTDB/
├── backend/          # FastAPI app, collectors, workers, tests
├── docs/             # README assets
├── frontend/         # React SPA
├── spec-sheets/      # Technical specifications
└── docker-compose.yml
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.13+ (optional, for local backend development)
- Node.js 20+ (optional, for local frontend development)

### Run the full stack

```bash
cp .env.example .env   # optional — Docker provides dev defaults for JWT/DB/Redis
docker compose up -d
```

Wait until the backend is healthy, then open the frontend:

```bash
docker compose ps
```

| Service    | URL                          |
|------------|------------------------------|
| Frontend   | http://localhost:5173        |
| API        | http://localhost:8000        |
| API Docs   | http://localhost:8000/docs   |
| PostgreSQL | localhost:5432               |
| Redis      | localhost:6379               |

On startup the backend bootstraps the database schema (Alembic), seeds a default organization, and starts the mock collector. The frontend waits for a healthy backend before starting.

### Verify in the browser

1. Open http://localhost:5173
2. Register a new account and organization
3. Open **Dashboard** — live mock events should stream via WebSocket
4. Open **Events** — query historical events with filters and pagination
5. Open **Settings** — view organization details
6. Change the dashboard chart symbol — layout persists via the dashboard API

### Stop the stack

```bash
docker compose down
```

To also remove persisted database data:

```bash
docker compose down -v
```

## Local development (without Docker app containers)

Run Postgres and Redis in Docker, then start the backend and frontend on the host:

```bash
# Dependencies
docker compose up -d postgres redis

# Backend
cd backend
cp .env.example .env
pip install -e ".[dev]"
python -m app.db.bootstrap
python -m app.db.seed
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
cp .env.example .env
npm install
npm run dev
```

When `VITE_API_BASE_URL` and `VITE_WS_BASE_URL` are empty, the Vite dev server proxies `/api` and `/ws` to `http://localhost:8000`.

## Configuration

Copy `.env.example` to `.env` at the repo root for local overrides. Docker Compose sets sensible defaults when `.env` is absent.

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `JWT_SECRET` | Secret for signing JWTs |
| `CORS_ORIGINS` | Comma-separated browser origins (default: `http://localhost:5173`) |
| `VITE_API_BASE_URL` | Frontend REST base URL (empty = use Vite proxy) |
| `VITE_WS_BASE_URL` | Frontend WebSocket base URL (empty = use Vite proxy) |

## Tests and quality checks

```bash
# Backend (requires postgres and redis)
cd backend
pip install -e ".[dev]"
pytest

# Frontend
cd frontend
npm install
npm run build
npm run lint
```

```bash
# Lint and type check (backend)
cd backend
ruff check .
black --check .
mypy app
```

## API overview

Base URL: `/api/v1` · WebSocket: `/ws/events?token=<access_token>`

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Service health |
| `POST /auth/register` | Register user and organization |
| `POST /auth/login` | Login |
| `POST /auth/refresh` | Refresh access token |
| `GET /organization` | Current organization |
| `POST /events` | Ingest event |
| `GET /events` | Query events (filters, pagination) |
| `GET /events/{id}` | Get single event |
| `GET /dashboards` | List dashboards |
| `POST /dashboards` | Create dashboard |
| `GET /dashboards/{id}` | Get dashboard |
| `PATCH /dashboards/{id}` | Update dashboard name/layout |
| `WS /ws/events?token=` | Live event stream |

See [OpenPulse-v0.1-spec.md](spec-sheets/OpenPulse-v0.1-spec.md) for the full specification.
