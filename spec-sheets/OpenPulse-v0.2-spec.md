# OpenPulse v0.2 — Technical Specification

> **Version:** 0.2  
> **Status:** Planned  
> **Last Updated:** 2026-07-10  
> **Type:** Open Market Terminal (event intelligence platform)
> **Builds on:** [OpenPulse-v0.1-spec.md](OpenPulse-v0.1-spec.md)

---

## 1. Vision

OpenPulse is an **open-source Bloomberg** — a market terminal built on an open, unified event model. The long-term goal is professional-grade market intelligence (live prices, macro data, news, alerts) with the accessibility and extensibility of open source.

v0.1 established OpenPulse as a working multi-tenant event platform with a mock data source, REST + WebSocket APIs, and a React frontend.

**v0.2 proves the architecture with real-world ingress** and takes the **first UX step toward a terminal feel:** replace the mock-only collector story with live market data, open programmatic event ingestion via API keys, add WebSocket filtering, and present market data with professional formatting instead of raw JSON.

The unified `Event` model from v0.1 remains the implementation strategy. The **user-facing north star** is a terminal where symbols, sources, and prices are first-class — not generic event blobs.

The frontend remains one consumer. External systems, collectors, and integrations all continue to communicate through the unified event model defined in v0.1.

### v0.2 Theme

**Real Data & External Access**

### Product positioning

| Layer | v0.2 focus |
|-------|------------|
| **North star** | Open-source Bloomberg — dense, market-native, symbol-centric |
| **Implementation** | Everything is still an Event; collectors normalize upstream data |
| **UX in v0.2** | First terminal polish: formatted prices, source badges, % change, source filters |
| **UX deferred** | Watchlists, command bar, multi-panel workspaces, keyboard shortcuts (v0.3+) |

---

## 2. Core Design Principles

v0.1 principles remain in force. v0.2 adds:

| # | Principle | Description |
|---|-----------|-------------|
| 11 | **Real sources plug in, mock stays** | Mock collector remains for zero-dependency local dev; real collectors are opt-in via configuration |
| 12 | **Market data is global** | Public market feeds (e.g. Binance spot tickers) fan out to all organizations; tenant isolation applies to persistence and delivery, not to duplicating upstream APIs per org |
| 13 | **API keys are org-scoped secrets** | Programmatic access uses hashed keys; plaintext is shown once at creation only |
| 14 | **Filter at the edge** | WebSocket clients declare interest; the server filters before push to reduce noise |
| 15 | **Symbol is the primary noun** | Users think in tickers; UI orbits around symbols, not raw event records |
| 16 | **Market-native presentation** | Prices, percentages, and sources are formatted for humans — never raw JSON in primary views |
| 17 | **Sources are visible** | Every event shows where it came from (`mock`, `binance`, `webhook`); users can filter by source |
| 18 | **Live by default** | The Dashboard is a terminal surface; REST is for history and export |

---

## 3. Tech Stack

### 3.1 Backend (unchanged from v0.1)

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
| Auth | JWT + API keys | JWT for users; API keys for `POST /events` |
| HTTP Client | httpx | Binance REST fallback / health probes |
| WebSocket Client | websockets | Binance spot ticker stream |
| Containerization | Docker | Docker Compose |

### 3.2 Frontend (unchanged from v0.1)

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

### 3.3 New in v0.2

| Component | Purpose |
|-----------|---------|
| `collectors/binance.py` | First real data collector |
| `collectors/registry.py` | Config-driven collector enablement |
| `api/v1/api_keys.py` | API key management routes |
| `auth/api_key.py` | API key verification dependency |
| `services/api_key.py` | API key business logic |
| `websocket/filters.py` | Per-connection event filter state |
| `utils/formatMarket.ts` | Price, percent, and currency formatters |
| `components/ui/SourceBadge.tsx` | Source chip for feed and table rows |
| `components/dashboard/SourceFilter.tsx` | All / mock / binance filter control |

### 3.4 Defer Until Post-v0.2

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
- Advanced analytics (OHLC aggregation, rollups)
- Additional collectors beyond mock + Binance (FRED, SEC, Congress, Kalshi)
- Per-organization collector configuration
- API key scopes / fine-grained permissions
- Watchlists and symbol command bar
- Multi-panel terminal workspaces
- Keyboard shortcuts and layout presets
- Full Bloomberg-style information density (news wire, fixed-income panels, etc.)

---

## 4. Repository Layout

Additions relative to v0.1:

```
openpulse/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   └── api_keys.py          # NEW
│   │   ├── auth/
│   │   │   └── api_key.py           # NEW — API key auth dependency
│   │   ├── collectors/
│   │   │   ├── binance.py           # NEW
│   │   │   └── registry.py          # NEW
│   │   ├── services/
│   │   │   └── api_key.py           # NEW
│   │   ├── schemas/
│   │   │   └── api_key.py           # NEW
│   │   └── websocket/
│   │       └── filters.py           # NEW
│   └── alembic/versions/
│       └── 002_api_key_last_used.py # NEW (optional column)
├── frontend/
│   └── src/
│       ├── api/apiKeys.ts           # NEW
│       ├── utils/
│       │   └── formatMarket.ts      # NEW — price / percent formatters
│       ├── components/
│       │   ├── ui/
│       │   │   └── SourceBadge.tsx  # NEW
│       │   ├── dashboard/
│       │   │   └── SourceFilter.tsx # NEW
│       │   └── settings/
│       │       └── ApiKeyManager.tsx    # NEW
│       └── types/apiKey.ts          # NEW
└── spec-sheets/
    └── OpenPulse-v0.2-spec.md
```

---

## 5. v0.2 Scope

### 5.1 Collector Registry

Replace the hardcoded `MockCollector` in `collector_loop.py` with a configuration-driven registry.

```python
class CollectorRegistry:
    """Resolve enabled collectors from settings."""

    def get_enabled(self) -> list[BaseCollector]:
        ...
```

**Configuration:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COLLECTORS` | No | `mock` | Comma-separated collector names: `mock`, `binance` |

**Rules:**

- At least one collector must be enabled in non-test environments
- Each collector implements `BaseCollector` unchanged from v0.1
- Collectors run concurrently as independent `asyncio` tasks
- Each collector owns its own reconnect/backoff loop

### 5.2 Binance Collector

The first real data source. Proves the collector plugin model against external APIs.

**Source:** Binance Spot WebSocket combined stream (`wss://stream.binance.com:9443/stream`)

**Symbols (v0.2):**

| OpenPulse symbol | Binance stream |
|------------------|----------------|
| `BTC` | `btcusdt@ticker` |
| `ETH` | `ethusdt@ticker` |

**Event mapping:**

```python
EventCreate(
    source="binance",
    event_type="price",
    symbol="BTC",           # base asset, not pair
    timestamp=<event_time>, # UTC, from Binance payload
    importance=3,
    payload={
        "price": <last_price>,
        "currency": "USD",
        "pair": "BTCUSDT",
        "change_24h_pct": <price_change_percent>,
    },
    metadata={
        "collector": "binance",
        "stream": "btcusdt@ticker",
        "asset_class": "crypto",
        "display_symbol": "BTC",
    },
)
```

**Display conventions (collectors should populate when known):**

| Field | Location | Purpose |
|-------|----------|---------|
| `payload.price` | payload | Last price (number) |
| `payload.currency` | payload | Quote currency (e.g. `USD`) |
| `payload.change_24h_pct` | payload | 24h change percent (Binance) |
| `metadata.asset_class` | metadata | `crypto`, `equity`, `macro`, etc. |
| `metadata.display_symbol` | metadata | Human-facing symbol (defaults to `symbol`) |

The event schema is unchanged. Terminal-friendly display is achieved through **payload/metadata conventions** and **frontend formatters** — not new ORM types.

**Behavior:**

- Connect to combined stream on startup
- Reconnect with exponential backoff on disconnect (max 30s)
- Parse ticker messages and yield `EventCreate` objects
- Never write to the database directly
- On collector error, log and retry; do not crash the application

**Fan-out model:**

- Same as v0.1 mock collector: each event is persisted and broadcast for **every organization**
- Rationale: public market data is identical for all tenants; avoids per-org Binance connections

**Configuration:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BINANCE_ENABLED` | No | `false` | Enable Binance collector (overridden by `COLLECTORS`) |
| `BINANCE_WS_URL` | No | `wss://stream.binance.com:9443/stream` | Binance WebSocket base URL |
| `BINANCE_SYMBOLS` | No | `BTC,ETH` | Comma-separated base symbols |

**Docker Compose (v0.2):**

```yaml
environment:
  COLLECTORS: mock,binance
```

Local dev without internet may use `COLLECTORS=mock` only.

### 5.3 API Keys

v0.1 created the `api_keys` table and stub repository. v0.2 completes the feature.

**Key format:**

```
op_live_<43-char-url-safe-random>
```

Example: `op_live_a8f3k2m9x1p4q7r0s5t2u6v8w1y3z5a7b9c2d4e6`

**Storage:**

- Store SHA-256 hash of the full key in `api_keys.hashed_key`
- Plaintext key returned **once** in the create response
- Prefix `op_live_` enables fast lookup before hash verification

**Optional schema addition (migration `002`):**

| Column | Type | Description |
|--------|------|-------------|
| `last_used_at` | TIMESTAMP NULL | Updated on each successful API key authentication |

### 5.4 API Key Authentication

API keys authenticate **programmatic event ingestion only** in v0.2.

| Endpoint | Auth methods |
|----------|--------------|
| `POST /events` | JWT Bearer **or** `X-API-Key` header |
| All other routes | JWT Bearer only (unchanged) |

**Header:**

```
X-API-Key: op_live_a8f3k2m9x1p4q7r0s5t2u6v8w1y3z5a7b9c2d4e6
```

**Flow:**

```
Request with X-API-Key
    ↓
hash(key) → ApiKeyRepository.get_by_hash()
    ↓
resolve organization_id
    ↓
EventService.create_event(organization_id, data)
```

Invalid or revoked keys return `401 AUTHENTICATION_ERROR`.

### 5.5 WebSocket Subscription Filtering

v0.1 deferred client → server messages. v0.2 adds optional subscription filters.

**Connection:** unchanged — `ws://host/ws/events?token=<access_token>`

**Client → Server (after connect):**

```json
{
  "type": "subscribe",
  "filters": {
    "symbol": "BTC",
    "source": "binance",
    "event_type": "price"
  }
}
```

All filter fields are optional. Omitted fields mean "no filter" (match all).

**Server behavior:**

- Default (no subscribe message): deliver all events for the organization (v0.1 behavior)
- After subscribe: only events matching **all** provided filters are pushed
- Filters may be updated by sending a new `subscribe` message
- Invalid JSON or unknown `type` → ignore message, keep connection open

**Server → Client:** unchanged from v0.1 (`{ "type": "event", "data": { ... } }`)

**Acknowledgement (optional but recommended):**

```json
{
  "type": "subscribed",
  "filters": {
    "symbol": "BTC",
    "source": "binance",
    "event_type": "price"
  }
}
```

### 5.6 Terminal UX (v0.2)

v0.2 is not a full terminal rebuild. It introduces **market-native presentation** on top of the existing Dashboard and Events pages so real data feels credible and Bloomberg-directional.

#### Design goals

- Users see **prices and percentages**, not `{"price":65000,"currency":"USD"}` in primary views
- Users can distinguish **mock vs real** data at a glance
- **Symbol** remains the anchor; source filter narrows the feed without leaving the Dashboard
- Information density increases slightly; layout structure from v0.1 is preserved

#### Shared formatting utilities

Add `frontend/src/utils/formatMarket.ts`:

| Function | Input | Output example |
|----------|-------|----------------|
| `formatPrice(value, currency?)` | `65000.25`, `USD` | `$65,000.25` |
| `formatPercent(value)` | `1.234` | `+1.23%` (green if ≥ 0, red if < 0) |
| `formatVolume(value)` | `1234567` | `1.23M` |

Use locale-aware `Intl.NumberFormat` where practical. Fall back to em dash (`—`) when a field is missing.

#### Source badges

Add `SourceBadge` component — a small chip on each event row:

| Source | Label | Color (Tailwind) |
|--------|-------|------------------|
| `mock` | Mock | `slate` (muted — clearly synthetic) |
| `binance` | Binance | `emerald` (live market data) |
| `webhook` / other | Title-cased source | `pulse` / neutral |

Used in: Live Event Feed, Events table, and optionally chart header.

#### Dashboard (`/dashboard`)

| Change | Description |
|--------|-------------|
| **Source filter** | Segmented control or dropdown: **All** / **Mock** / **Binance** |
| **Default filter** | When `binance` collector is enabled, default to **Binance** (not All) so first load shows real market data |
| **WebSocket subscribe** | Send `subscribe` message when symbol or source filter changes |
| **Live Event Feed columns** | Replace raw Payload column with: **Price**, **Change**, **Source** (badge) |
| **Formatted prices** | Price column uses `formatPrice()` from `payload.price` + `payload.currency` |
| **% change column** | Show `formatPercent(payload.change_24h_pct)` when present; `—` otherwise |
| **Price chart** | Y-axis and tooltip use `formatPrice()`; chart title shows active symbol + source badge |
| **Statistics** | `sources` count reflects active collectors; no change to layout |
| **Subtitle** | Update header subtitle from "Event Intelligence" to **"Market Terminal"** (AppLayout) |

**Live Event Feed column spec (v0.2):**

| Column | Content |
|--------|---------|
| Time | `HH:mm:ss` local |
| Symbol | Bold ticker |
| Price | Formatted price or `—` |
| Change | Formatted % or `—` |
| Source | `SourceBadge` |
| Type | `price` / `volume` (secondary text) |

Raw JSON payload moves to an expandable row detail or tooltip — not the default column.

#### Events page (`/events`)

| Change | Description |
|--------|-------------|
| **Source filter** | Preset chips: All / mock / binance (maps to existing `source` query param) |
| **Columns** | Add **Price**, **Change**, **Source** (badge); demote raw Payload to expandable detail |
| **Formatting** | Same `formatMarket` utilities as Dashboard |

#### Settings page (`/settings`)

Replace the v0.2 placeholder with a functional API key manager:

| Action | UI |
|--------|-----|
| List keys | Table: name, created_at, last_used_at (if available), revoke button |
| Create key | Modal/form: name input → show full key once with copy button |
| Revoke key | Confirm dialog → `DELETE` |

### 5.7 Terminal UX Roadmap (post-v0.2)

v0.2 delivers **credible market presentation**. Later versions build toward a full open-source Bloomberg terminal:

| Version | Terminal UX milestone |
|---------|----------------------|
| **v0.2** | Formatted prices, % change, source badges, mock vs binance filter |
| **v0.3** | Watchlist (pinned symbols), symbol search / command bar |
| **v0.4** | Multi-panel linked workspace (feed + chart + stats follow active symbol) |
| **v0.5** | News / macro events (FRED), alert strip |
| **v0.6** | Keyboard shortcuts, layout presets ("Trading", "Macro") |

These are **not** in v0.2 scope; listed here to align implementation with the product north star.

---

## 6. Database Schema

### 6.1 `api_keys` (migration `002` — additive only)

Existing columns from v0.1 are unchanged. Add:

| Column | Type | Constraints |
|--------|------|-------------|
| `last_used_at` | TIMESTAMP | UTC, NULLABLE |

No other tables are modified in v0.2.

---

## 7. API Specification

**Base URL:** `/api/v1/` (unchanged)

### 7.1 Events (updated)

#### `POST /events`

**Authentication:** JWT Bearer **or** `X-API-Key` header.

When using an API key, the event is created for the key's organization. Request body unchanged from v0.1.

**Example with API key:**

```http
POST /api/v1/events
X-API-Key: op_live_a8f3k2m9x1p4q7r0s5t2u6v8w1y3z5a7b9c2d4e6
Content-Type: application/json

{
  "source": "webhook",
  "event_type": "price",
  "symbol": "BTC",
  "timestamp": "2026-07-10T12:00:00Z",
  "importance": 3,
  "payload": { "price": 65000.00 },
  "metadata": { "client": "zapier" }
}
```

### 7.2 API Keys (new)

#### `GET /api-keys`

List API keys for the current organization. **Never returns plaintext keys.**

**Response:**

```json
[
  {
    "id": "uuid",
    "organization_id": "uuid",
    "name": "Production webhook",
    "created_at": "2026-07-10T12:00:00Z",
    "last_used_at": null
  }
]
```

#### `POST /api-keys`

Create a new API key.

**Request:**

```json
{
  "name": "Production webhook"
}
```

**Response (201):**

```json
{
  "id": "uuid",
  "organization_id": "uuid",
  "name": "Production webhook",
  "key": "op_live_a8f3k2m9x1p4q7r0s5t2u6v8w1y3z5a7b9c2d4e6",
  "created_at": "2026-07-10T12:00:00Z"
}
```

The `key` field is present **only** in this response.

#### `DELETE /api-keys/{id}`

Revoke an API key. Returns `204 No Content`.

Returns `404 NOT_FOUND` if the key does not belong to the current organization.

### 7.3 Unchanged Endpoints

All v0.1 endpoints remain unchanged unless noted above:

- `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`
- `GET /organization`
- `GET /events`, `GET /events/{id}`
- `GET /dashboards`, `POST /dashboards`, `GET /dashboards/{id}`, `PATCH /dashboards/{id}`
- `GET /health`
- `WS /ws/events?token=`

---

## 8. WebSocket Specification

### 8.1 Endpoint

```
ws://host/ws/events?token=<access_token>
```

Unchanged from v0.1.

### 8.2 Authentication

Unchanged — JWT access token as query parameter.

### 8.3 Server → Client Messages

Unchanged from v0.1.

### 8.4 Client → Server Messages (new in v0.2)

#### Subscribe / update filters

```json
{
  "type": "subscribe",
  "filters": {
    "symbol": "BTC",
    "source": "binance",
    "event_type": "price"
  }
}
```

#### Server acknowledgement

```json
{
  "type": "subscribed",
  "filters": {
    "symbol": "BTC",
    "source": "binance",
    "event_type": "price"
  }
}
```

---

## 9. Collector Pipeline

v0.1 pipeline is unchanged. v0.2 runs multiple collectors in parallel:

```
CollectorRegistry.get_enabled()
    ↓
[MockCollector, BinanceCollector]  (concurrent asyncio tasks)
    ↓
collect()
    ↓
validate()        # EventCreate.model_validate
    ↓
persist()         # per organization (fan-out)
    ↓
broadcast()       # Redis pub/sub per organization
    ↓
WebSocket push    # with per-connection filters applied
```

---

## 10. Background Tasks

### 10.1 Collector Loop (updated)

```python
async def run_collector_loops(redis: Redis) -> None:
    registry = CollectorRegistry(settings)
    collectors = registry.get_enabled()
    tasks = [
        asyncio.create_task(run_single_collector(collector, redis))
        for collector in collectors
    ]
    await asyncio.gather(*tasks)
```

Each `run_single_collector` mirrors v0.1 fan-out behavior for its collector's events.

### 10.2 Implementation

Continue using `asyncio` tasks embedded in the FastAPI lifespan. No Celery.

---

## 11. Configuration

New and updated environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COLLECTORS` | No | `mock` | Enabled collectors: `mock`, `binance` (comma-separated) |
| `BINANCE_ENABLED` | No | `false` | Deprecated alias; use `COLLECTORS` |
| `BINANCE_WS_URL` | No | `wss://stream.binance.com:9443/stream` | Binance WebSocket URL |
| `BINANCE_SYMBOLS` | No | `BTC,ETH` | Symbols to subscribe |

All v0.1 variables remain unchanged.

**Example `.env` for v0.2 development:**

```env
COLLECTORS=mock,binance
JWT_SECRET=change-me-in-production-use-a-long-random-string
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

## 12. Error Responses

Unchanged from v0.1. New cases:

| Code | HTTP Status | When |
|------|-------------|------|
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing `X-API-Key` on `POST /events` |
| `NOT_FOUND` | 404 | API key ID not found for DELETE |

---

## 13. Coding Standards

Unchanged from v0.1. Additional rules for v0.2:

| Rule | Enforcement |
|------|-------------|
| Collectors never import repositories | Required |
| API key plaintext never logged or persisted | Required |
| Binance collector covered by tests with mocked WebSocket | Required |
| WebSocket filter logic isolated in `websocket/filters.py` | Required |
| Market formatters centralized in `utils/formatMarket.ts` | Required |
| Primary tables/feeds must not show raw JSON payloads by default | Required |

---

## 14. Definition of Done (v0.2)

### Backend & data

- [ ] `COLLECTORS=mock,binance` runs both collectors in Docker Compose
- [ ] Binance spot ticker events for BTC and ETH appear on the Dashboard live feed
- [ ] Binance events include `payload.change_24h_pct` and `metadata.asset_class`
- [ ] Mock collector still works with `COLLECTORS=mock` (offline dev)
- [ ] `POST /api-keys` creates a key; plaintext shown once; hash stored
- [ ] `GET /api-keys` lists keys without exposing secrets
- [ ] `DELETE /api-keys/{id}` revokes a key
- [ ] `POST /events` accepts `X-API-Key` and creates events for the key's organization
- [ ] Revoked keys are rejected with `401`
- [ ] WebSocket clients can send `subscribe` with symbol/source/event_type filters
- [ ] Alembic migration `002` applied (if `last_used_at` column added)

### Terminal UX

- [ ] Live Event Feed shows **formatted price** and **% change** columns (not raw JSON)
- [ ] **Source badges** appear on Dashboard feed and Events table rows
- [ ] Dashboard **source filter** supports All / Mock / Binance; defaults to Binance when enabled
- [ ] Dashboard sends WebSocket `subscribe` when symbol or source filter changes
- [ ] Price chart tooltips and axis use formatted currency values
- [ ] Events page has source preset filters and matching formatted columns
- [ ] App header subtitle reads **"Market Terminal"**
- [ ] Settings page manages API keys (no placeholder text)

### Quality

- [ ] Unit/integration tests cover:
  - [ ] Binance collector message parsing (mocked stream)
  - [ ] API key create, authenticate, revoke
  - [ ] WebSocket filter matching
  - [ ] Collector registry enable/disable
  - [ ] `formatMarket` utilities (price, percent edge cases)
- [ ] README updated for v0.2 configuration and terminal UX
- [ ] All v0.1 tests continue to pass

---

## 15. What NOT to Build in v0.2

To maintain focus:

- ❌ RBAC or user roles
- ❌ Alert rules or notification delivery
- ❌ Celery, Kafka, RabbitMQ, NATS
- ❌ TimescaleDB or ClickHouse
- ❌ Second real collector (FRED, SEC, etc.)
- ❌ Per-organization collector configuration
- ❌ API key scopes or rate limiting
- ❌ OHLC aggregation or analytics rollups
- ❌ Plugin auto-discovery
- ❌ Kubernetes or multi-node deployment
- ❌ Machine learning or anomaly detection
- ❌ Watchlists, command bar, keyboard shortcuts
- ❌ Multi-panel terminal workspaces

> **Goal:** Prove real-world data ingress and programmatic access, and make the UI feel like the first pane of an open-source Bloomberg terminal — without breaking v0.1 abstractions. v0.3 adds watchlists, a second collector family, and basic alerting.

---

## 16. Development Workflow

```bash
# 1. Start the stack with real + mock collectors
cp .env.example .env
# Set COLLECTORS=mock,binance in .env or docker-compose.yml
docker compose up -d

# 2. Verify Binance events and terminal UX
curl http://localhost:8000/api/v1/health
# Open http://localhost:5173 → Dashboard
# - Source filter: Binance
# - Feed shows formatted prices, % change, source badges (not raw JSON)

# 3. Create an API key (browser or curl with JWT)
curl -X POST http://localhost:8000/api/v1/api-keys \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "test-key"}'

# 4. Ingest via API key
curl -X POST http://localhost:8000/api/v1/events \
  -H "X-API-Key: op_live_..." \
  -H "Content-Type: application/json" \
  -d '{"source":"webhook","event_type":"price","symbol":"BTC","timestamp":"2026-07-10T12:00:00Z","importance":3,"payload":{},"metadata":{}}'

# 5. Run tests
cd backend && pytest
cd frontend && npm run build && npm run lint
```

---

## 17. v0.3+ Preview

| Feature | Rationale |
|---------|-----------|
| **Watchlist + symbol command bar** | Core terminal workflow: type a ticker, all panels follow |
| FRED macro collector | Different API cadence than Binance; validates second collector pattern |
| Basic alert rules | Importance threshold on incoming events |
| Multi-panel linked workspace | Feed, chart, and stats share active symbol |
| Event aggregation (OHLC) | Requires sustained real data volume |
| Per-org collector config | Needed when tenants bring private data sources |
| Keyboard shortcuts & layout presets | Professional terminal power-user UX |

---

*End of Specification*
