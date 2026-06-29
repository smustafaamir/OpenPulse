"""Health endpoint tests."""

from httpx import AsyncClient


async def test_health(client: AsyncClient) -> None:
    """Health check returns healthy status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data
