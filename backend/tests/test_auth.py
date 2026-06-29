"""Authentication endpoint tests."""

from httpx import AsyncClient


async def _register(
    client: AsyncClient,
    email: str = "user@example.com",
    password: str = "securepass",
    org_name: str = "Acme Corp",
):
    """Helper to register a user."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "organization_name": org_name,
        },
    )
    return response


async def test_register_login_refresh(client: AsyncClient) -> None:
    """Register, login, and refresh tokens."""
    reg = await _register(client)
    assert reg.status_code == 200
    tokens = reg.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "securepass"},
    )
    assert login.status_code == 200
    login_tokens = login.json()
    assert login_tokens["access_token"]

    refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh.status_code == 200
    assert refresh.json()["access_token"]


async def test_register_duplicate_email(client: AsyncClient) -> None:
    """Duplicate registration returns conflict."""
    await _register(client)
    response = await _register(client, email="user@example.com")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


async def test_login_invalid_credentials(client: AsyncClient) -> None:
    """Invalid login returns authentication error."""
    await _register(client, email="other@example.com")
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "other@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
