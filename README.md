# OpenPulse

Open-source, multi-tenant event intelligence platform.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.13+ (for local backend development without Docker)
- Node.js 20+ (for local frontend development without Docker)

### Run the full stack

```bash
cp .env.example .env
docker compose up -d
```

Services:

| Service    | URL                          |
|------------|------------------------------|
| Frontend   | http://localhost:5173        |
| API        | http://localhost:8000        |
| API Docs   | http://localhost:8000/docs   |
| PostgreSQL | localhost:5432               |
| Redis      | localhost:6379               |

On startup the backend runs Alembic migrations, seeds the default organization, and starts the mock collector (~1 event/sec for every organization).

### Verify v0.1 in the browser

1. Open http://localhost:5173
2. Register a new account and organization
3. Sign in and open **Dashboard** — live mock events should stream via WebSocket
4. Open **Events** — query historical events with filters and pagination
5. Open **Settings** — view organization details
6. Change the dashboard chart symbol — layout persists via dashboard API

### Local development (without Docker app containers)

```bash
# Start dependencies only
docker compose up -d postgres redis

# Backend
cd backend
cp .env.example .env
pip install -e ".[dev]"
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
cp .env.example .env
npm install
npm run dev
```

The Vite dev server proxies `/api` and `/ws` to `http://localhost:8000` when `VITE_*` URLs are left empty.

### Run tests

```bash
# Backend (requires postgres and redis)
cd backend
pip install -e ".[dev]"
pytest

# Frontend build check
cd frontend
npm install
npm run build
```

### Lint and type check

```bash
cd backend
ruff check .
black --check .
mypy app

cd ../frontend
npm run lint
```

## API Overview

Base URL: `/api/v1`

| Endpoint              | Description              |
|-----------------------|--------------------------|
| `GET /health`         | Service health           |
| `POST /auth/register`   | Register user + org      |
| `POST /auth/login`      | Login                    |
| `POST /auth/refresh`    | Refresh access token     |
| `GET /organization`     | Current organization     |
| `POST /events`          | Ingest event             |
| `GET /events`           | Query events             |
| `GET /events/{id}`      | Get single event         |
| `GET /dashboards`       | List dashboards          |
| `POST /dashboards`      | Create dashboard         |
| `GET /dashboards/{id}`  | Get dashboard            |
| `PATCH /dashboards/{id}` | Update dashboard      |
| `WS /ws/events?token=`  | Live event stream        |

See [OpenPulse-v0.1-spec.md](spec-sheets/OpenPulse-v0.1-spec.md) for the full specification.
