"""Event endpoint tests."""

from datetime import UTC, datetime

from httpx import AsyncClient


async def _auth_headers(client: AsyncClient) -> dict[str, str]:
    """Register and return authorization headers."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "events@example.com",
            "password": "securepass",
            "organization_name": "Events Org",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "events@example.com", "password": "securepass"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_and_list_events(client: AsyncClient) -> None:
    """Ingest and query events."""
    headers = await _auth_headers(client)
    event_payload = {
        "source": "custom",
        "event_type": "price",
        "symbol": "BTC",
        "timestamp": datetime.now(UTC).isoformat(),
        "importance": 3,
        "payload": {"price": 65000.0, "currency": "USD"},
        "metadata": {"client": "webhook"},
    }
    create = await client.post("/api/v1/events", json=event_payload, headers=headers)
    assert create.status_code == 201
    created = create.json()
    assert created["symbol"] == "BTC"
    assert created["source"] == "custom"

    listing = await client.get("/api/v1/events?symbol=BTC", headers=headers)
    assert listing.status_code == 200
    data = listing.json()
    assert data["total"] >= 1
    assert data["items"][0]["symbol"] == "BTC"

    single = await client.get(f"/api/v1/events/{created['id']}", headers=headers)
    assert single.status_code == 200
    assert single.json()["id"] == created["id"]


async def test_event_tenant_isolation(client: AsyncClient) -> None:
    """Users cannot access events from another organization."""
    headers_a = await _auth_headers(client)

    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "other@example.com",
            "password": "securepass",
            "organization_name": "Other Org",
        },
    )
    login_b = await client.post(
        "/api/v1/auth/login",
        json={"email": "other@example.com", "password": "securepass"},
    )
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    create = await client.post(
        "/api/v1/events",
        json={
            "source": "custom",
            "event_type": "price",
            "symbol": "ETH",
            "timestamp": datetime.now(UTC).isoformat(),
            "importance": 2,
            "payload": {},
            "metadata": {},
        },
        headers=headers_a,
    )
    event_id = create.json()["id"]

    response = await client.get(f"/api/v1/events/{event_id}", headers=headers_b)
    assert response.status_code == 404
