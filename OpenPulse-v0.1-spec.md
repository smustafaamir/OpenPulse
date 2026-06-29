# OpenPulse v0.1 — Technical Specification

> **Version:** 0.1  
> **Status:** MVP  
> **Last Updated:** 2026-06-28  
> **Type:** Event Intelligence Platform

---

## 1. Vision

OpenPulse is an open-source, multi-tenant event intelligence platform.

Rather than specializing in one domain, OpenPulse treats every incoming piece of information as an **Event**. Data providers, analytics engines, dashboards, alerts, and third-party integrations all communicate through this unified event model.

The frontend is only one consumer of the platform. APIs, WebSockets, CLI tools, and SDKs should all expose the same capabilities.

---

## 2. Core Design Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Everything is an Event** | All data flows through the unified event model |
| 2 | **Every data source is a plugin** | Collectors are swappable, independent components |
| 3 | **Every component is independently replaceable** | No hard dependencies between layers |
| 4 | **Multi-tenancy is a first-class feature** | Organizations isolate all data |
| 5 | **APIs remain stable while implementations evolve** | Versioned, contract-first design |
| 6 | **Docker-first development** | Entire stack runs via Docker Compose |
| 7 | **Zero-cost local development** | No external dependencies for local work |
| 8 | **Fully typed Python** | Type hints everywhere |
| 9 | **Async wherever possible** | Non-blocking I/O by default |
| 10 | **Open-source friendly architecture** | Clean abstractions, clear boundaries |

---

## 3. Tech Stack

### 3.1 Backend

| Component | Technology | Version/Notes |
|-----------|------------|---------------|
| Language | Python | 3.13+ |
| Web Framework | FastAPI | Latest stable |
| ORM | SQLAlchemy 2 | Async support |
| Migrations | Alembic | — |
| Validation | Pydantic v2 | — |
| Database Driver | asyncpg | For PostgreSQL |
| Database | PostgreSQL | 15+ |
| Cache/PubSub | Redis | Pub/sub only; no Celery |
| Realtime | FastAPI WebSockets | Native |
| Auth | JWT | Access + Refresh tokens |
| Containerization | Docker | Docker Compose |

### 3.2 Frontend

| Component | Technology |
|-----------|------------|
| Framework | React |
| Language | TypeScript |
| Build Tool | Vite |
| Data Fetching | TanStack Query |
| Routing | React Router |
| State Management | Zustand |
| Styling | Tailwind CSS |
| Charts | Recharts |

### 3.3 Defer Until Post-MVP

- Celery or distributed workers
- Kafka, RabbitMQ, or NATS
- TimescaleDB or ClickHouse
- Kubernetes
- Role-based access control (RBAC)
- Alert engine
- Notification system
- Plugin auto-discovery
- Multi-node scaling
- Machine learning / anomaly detection
- Advanced analytics
- Multi-source collectors beyond mock

---

## 4. Repository Layout

```
openpulse/
├── backend/
│   ├── app/
│   │   ├── api/              # Route handlers
│   │   ├── auth/             # Authentication logic
│   │   ├── collectors/       # Data collectors
│   │   ├── core/             # Core utilities, config
│   │   ├── db/               # Database setup, session management
│   │   ├── events/           # Event processing pipeline
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── repositories/     # Data access layer
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── services/         # Business logic layer
│   │   ├── websocket/        # WS handlers
│   │   ├── workers/          # Background tasks
│   │   └── main.py           # Application entry point
│   └── tests/                # Unit & integration tests
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Route-level pages
│   │   ├── hooks/            # Custom React hooks
│   │   ├── stores/           # Zustand state stores
│   │   ├── api/              # API client functions
│   │   ├── websocket/        # WS connection management
│   │   └── types/            # TypeScript type definitions
│   └── public/
├── docker/                   # Docker configurations
├── docs/                     # Documentation
└── docker-compose.yml        # Full stack orchestration
```

---

## 5. MVP Scope

### 5.1 Authentication

- [ ] User registration (`POST /auth/register`)
- [ ] User login (`POST /auth/login`)
- [ ] JWT access tokens
- [ ] JWT refresh tokens (`POST /auth/refresh`)

### 5.2 Organizations

- Each user belongs to exactly one organization
- Organization → Users → Dashboards → Events → API Keys
- **No RBAC yet** — everyone is admin within their org

### 5.3 Event Model

Everything uses this exact structure. No inheritance, no subclasses, no polymorphism.

```python
class Event:
    id: UUID
    organization_id: UUID
    source: str           # e.g., "mock", "binance"
    event_type: str       # e.g., "price", "volume"
    symbol: str           # e.g., "BTC", "ETH", "SPY", "NVDA"
    timestamp: datetime   # UTC
    importance: int       # 1-5 scale
    payload: dict         # JSONB — flexible data
    metadata: dict        # JSONB — collector metadata
    created_at: datetime  # UTC
```

Every collector emits this exact structure.

### 5.4 Collector Interface

```python
class BaseCollector:
    source: str

    async def collect(self) -> AsyncIterator[Event]:
        """Yield events. Never talk directly to the database."""
        yield Event(...)
```

### 5.5 Collector Manager Pipeline

```
Collector
    ↓
collect()
    ↓
validate()
    ↓
publish()
    ↓
persist()
    ↓
broadcast()
```

The manager owns the entire pipeline. Collectors only emit events.

### 5.6 Initial Collectors

**Only one collector for v0.1: Mock Collector**

- Generates random events every second
- Symbols: `BTC`, `ETH`, `SPY`, `NVDA`
- Random values for price/volume fields
- Purpose: Build the platform before depending on external APIs

**Future collectors:** Binance, FRED, SEC, Congress, Kalshi

---

## 6. Database Schema

### 6.1 `organizations`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK |
| `name` | VARCHAR | NOT NULL |
| `created_at` | TIMESTAMP | UTC, DEFAULT NOW() |

### 6.2 `users`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK |
| `organization_id` | UUID | FK → organizations.id |
| `email` | VARCHAR | UNIQUE, NOT NULL |
| `password_hash` | VARCHAR | NOT NULL |
| `created_at` | TIMESTAMP | UTC, DEFAULT NOW() |

### 6.3 `events`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK |
| `organization_id` | UUID | FK → organizations.id |
| `source` | VARCHAR | NOT NULL |
| `event_type` | VARCHAR | NOT NULL |
| `symbol` | VARCHAR | NOT NULL |
| `timestamp` | TIMESTAMP | UTC, NOT NULL |
| `importance` | INTEGER | NOT NULL |
| `payload` | JSONB | NOT NULL, DEFAULT '{}' |
| `metadata` | JSONB | NOT NULL, DEFAULT '{}' |
| `created_at` | TIMESTAMP | UTC, DEFAULT NOW() |

### 6.4 `dashboards`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK |
| `organization_id` | UUID | FK → organizations.id |
| `name` | VARCHAR | NOT NULL |
| `layout` | JSONB | NOT NULL, DEFAULT '{}' |

### 6.5 `api_keys`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK |
| `organization_id` | UUID | FK → organizations.id |
| `name` | VARCHAR | NOT NULL |
| `hashed_key` | VARCHAR | NOT NULL |
| `created_at` | TIMESTAMP | UTC, DEFAULT NOW() |

---

## 7. API Specification

**Base URL:** `/api/v1/`

All routes prefixed with `/api/v1/` even though there's only one version.

### 7.1 Authentication

#### `POST /auth/register`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "organization_name": "Acme Corp"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### `POST /auth/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### `POST /auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### 7.2 Organizations

#### `GET /organization`

Returns the current user's organization.

**Response:**
```json
{
  "id": "uuid",
  "name": "Acme Corp",
  "created_at": "2026-06-28T00:00:00Z"
}
```

### 7.3 Events

#### `POST /events`

Ingest a new event (primarily for external sources; mock collector uses internal pipeline).

**Request:**
```json
{
  "source": "custom",
  "event_type": "price",
  "symbol": "BTC",
  "timestamp": "2026-06-28T12:00:00Z",
  "importance": 3,
  "payload": { "price": 65000.00, "currency": "USD" },
  "metadata": { "client": "webhook" }
}
```

**Response:**
```json
{
  "id": "uuid",
  "organization_id": "uuid",
  "source": "custom",
  "event_type": "price",
  "symbol": "BTC",
  "timestamp": "2026-06-28T12:00:00Z",
  "importance": 3,
  "payload": { "price": 65000.00 },
  "metadata": { "client": "webhook" },
  "created_at": "2026-06-28T12:00:01Z"
}
```

#### `GET /events`

Query historical events with filtering.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | string | Filter by symbol (e.g., `BTC`) |
| `source` | string | Filter by source (e.g., `mock`) |
| `event_type` | string | Filter by event type |
| `start` | ISO datetime | Start of time range |
| `end` | ISO datetime | End of time range |
| `limit` | integer | Max results (default: 100) |
| `offset` | integer | Pagination offset |

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "organization_id": "uuid",
      "source": "mock",
      "event_type": "price",
      "symbol": "BTC",
      "timestamp": "2026-06-28T12:00:00Z",
      "importance": 3,
      "payload": { "price": 65000.00 },
      "metadata": {},
      "created_at": "2026-06-28T12:00:01Z"
    }
  ],
  "total": 1000,
  "limit": 100,
  "offset": 0
}
```

#### `GET /events/{id}`

Get a single event by ID.

### 7.4 Dashboards

#### `GET /dashboards`

List all dashboards for the organization.

**Response:**
```json
[
  {
    "id": "uuid",
    "organization_id": "uuid",
    "name": "Main Dashboard",
    "layout": { "widgets": [...] }
  }
]
```

#### `POST /dashboards`

Create a new dashboard.

**Request:**
```json
{
  "name": "Main Dashboard",
  "layout": { "widgets": [] }
}
```

### 7.5 Health

#### `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-06-28T12:00:00Z"
}
```

---

## 8. WebSocket Specification

### 8.1 Endpoint

```
ws://host/ws/events
```

### 8.2 Authentication

Pass JWT token as query parameter: `?token=eyJ...`

### 8.3 Server → Client Messages

Every new event is broadcast to all connected clients:

```json
{
  "type": "event",
  "data": {
    "id": "uuid",
    "source": "mock",
    "event_type": "price",
    "symbol": "BTC",
    "timestamp": "2026-06-28T12:00:00Z",
    "importance": 3,
    "payload": { "price": 65000.00 },
    "metadata": {}
  }
}
```

### 8.4 Client → Server Messages

Not required for v0.1. Filtering can be added later.

---

## 9. Frontend Specification

### 9.1 Pages

| Page | Route | Description |
|------|-------|-------------|
| **Login** | `/login` | JWT login form |
| **Dashboard** | `/dashboard` | Live feed, charts, statistics |
| **Events** | `/events` | Table, search, filters |
| **Settings** | `/settings` | API keys, organization info |

### 9.2 Dashboard Widgets

| Widget | Description |
|--------|-------------|
| **Live Event Feed** | Newest 100 events, auto-updating |
| **Price Chart** | Realtime line chart (Recharts) |
| **Statistics** | Events received, events/minute, sources count, symbols count |

### 9.3 State Management

- **Zustand:** Global auth state, UI preferences
- **TanStack Query:** Server state (events, dashboards), caching, background refetch

### 9.4 WebSocket Integration

- Connect on Dashboard mount
- Reconnect with exponential backoff
- Buffer events while disconnected
- Display connection status indicator

---

## 10. Background Tasks

### 10.1 Mock Collector Loop

Runs every second:

```
Mock Collector
    ↓
generate Event (BTC, ETH, SPY, NVDA with random values)
    ↓
store Event (via EventService → EventRepository)
    ↓
broadcast Event (via WebSocket manager)
```

### 10.2 Implementation

Use FastAPI `BackgroundTasks` for v0.1. No Celery.

---

## 11. Services Layer Architecture

**Strict layering. Never access SQLAlchemy directly from routes.**

```
Routes (API Handlers)
    ↓
Services (Business Logic)
    ↓
Repositories (Persistence)
    ↓
Database (PostgreSQL)
```

### 11.1 Example Flow

```
POST /events
    ↓
EventService.create_event()
    ↓
EventRepository.insert()
    ↓
Database commit
```

---

## 12. Configuration

All configuration via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `REDIS_URL` | Yes | — | Redis connection string |
| `JWT_SECRET` | Yes | — | Secret key for JWT signing |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE` | No | `15` | Access token expiry (minutes) |
| `REFRESH_TOKEN_EXPIRE` | No | `7` | Refresh token expiry (days) |
| `ENV` | No | `development` | Environment name |
| `LOG_LEVEL` | No | `INFO` | Logging level |

---

## 13. Logging Specification

### 13.1 Format

Structured JSON logging. Every log entry includes:

```json
{
  "timestamp": "2026-06-28T12:00:00.000Z",
  "level": "INFO",
  "request_id": "uuid",
  "organization_id": "uuid",
  "route": "GET /api/v1/events",
  "duration_ms": 45.2,
  "message": "Fetched 100 events"
}
```

### 13.2 Requirements

- All logs output as JSON
- Include `request_id` for tracing
- Include `organization_id` for multi-tenant debugging
- Log request duration

---

## 14. Error Responses

Consistent error format across all endpoints:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "symbol": "Field required"
    }
  }
}
```

### 14.1 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Pydantic validation failure |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing token |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `INTERNAL_ERROR` | 500 | Unhandled server error |

---

## 15. Coding Standards

| Rule | Enforcement |
|------|-------------|
| Full type hints | Required on all public functions/classes |
| Linting | Ruff |
| Formatting | Black |
| Type checking | mypy — strict mode |
| Docstrings | Google-style for all public APIs |
| Database access | Async only (asyncpg) |
| Business logic | Never in route handlers |
| Persistence | Repository pattern only |
| Dependencies | Dependency injection for services |
| Timestamps | UTC everywhere |
| Flexible schemas | JSONB for event payloads/metadata |
| Documentation | Every public class/function documented |

---

## 16. Definition of Done (v0.1)

- [ ] `docker-compose up` brings up the entire stack with one command
- [ ] Users can register and log in via the frontend
- [ ] Mock collector generates random events every second
- [ ] Events are persisted to PostgreSQL
- [ ] Frontend displays new events live via WebSockets
- [ ] Users can query historical events through the REST API
- [ ] Dashboards are persisted and reload correctly
- [ ] All routes are documented via OpenAPI (auto-generated by FastAPI)
- [ ] Basic unit tests cover:
  - [ ] Authentication (register, login, refresh)
  - [ ] Event ingestion (mock collector → database)
  - [ ] Repository logic (CRUD operations)

---

## 17. What NOT to Build Yet

To keep momentum and avoid premature complexity, explicitly defer these until the foundation is stable:

- ❌ Celery or distributed workers
- ❌ Kafka, RabbitMQ, or NATS
- ❌ TimescaleDB or ClickHouse
- ❌ Kubernetes
- ❌ Role-based access control (RBAC)
- ❌ Alert engine
- ❌ Notification system
- ❌ Plugin auto-discovery
- ❌ Multi-node scaling
- ❌ Machine learning or anomaly detection
- ❌ Advanced analytics
- ❌ Multi-source collectors beyond the mock implementation

> **Goal:** Produce a clean, extensible event platform — not a feature-complete financial terminal. Once v0.1 is complete, incrementally replace the mock collector with real providers (Binance, FRED), add aggregation workers, introduce alerting, and evolve the architecture without breaking core abstractions.

---

## 18. Development Workflow

```bash
# 1. Clone and start the stack
git clone <repo>
cd openpulse
docker-compose up -d

# 2. Run backend tests
cd backend
pytest

# 3. Run frontend dev server
cd frontend
npm install
npm run dev

# 4. Access the app
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
# API:      http://localhost:8000/api/v1/
```

---

*End of Specification*
