# OpenPulse

Open-source, multi-tenant event intelligence platform.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.13+ (for local development without Docker)

### Run the full stack

```bash
cp .env.example .env
docker compose up -d
```

Services:

| Service    | URL                          |
|------------|------------------------------|
| API        | http://localhost:8000        |
| API Docs   | http://localhost:8000/docs   |
| PostgreSQL | localhost:5432               |
| Redis      | localhost:6379               |

On startup the backend runs Alembic migrations, seeds the default organization, and starts the mock collector (~1 event/sec).

### Local development (without Docker backend)

```bash
# Start dependencies only
docker compose up -d postgres redis

cd backend
cp .env.example .env
pip install -e ".[dev]"
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```

### Run tests

```bash
# Requires postgres and redis (docker compose up -d postgres redis)
cd backend
pip install -e ".[dev]"
pytest
```

### Lint and type check

```bash
cd backend
ruff check .
black --check .
mypy app
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
| `WS /ws/events?token=`  | Live event stream        |

See [OpenPulse-v0.1-spec.md](OpenPulse-v0.1-spec.md) for the full specification.
