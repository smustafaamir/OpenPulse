"""JWT and password utilities."""

from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import Settings
from app.core.exceptions import AuthenticationError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return cast(str, pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return cast(bool, pwd_context.verify(plain_password, hashed_password))


def create_access_token(
    user_id: UUID,
    organization_id: UUID,
    settings: Settings,
) -> str:
    """Create a short-lived access token."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire)
    payload = {
        "sub": str(user_id),
        "org_id": str(organization_id),
        "exp": expire,
        "type": "access",
    }
    return cast(
        str, jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    )


def create_refresh_token(user_id: UUID, settings: Settings) -> str:
    """Create a long-lived refresh token."""
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return cast(
        str, jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    )


def decode_token(token: str, settings: Settings) -> dict[str, Any]:
    """Decode and validate a JWT."""
    try:
        return cast(
            dict[str, Any],
            jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            ),
        )
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired token") from exc


def decode_access_token(token: str, settings: Settings) -> tuple[UUID, UUID]:
    """Decode an access token and return user_id and organization_id."""
    payload = decode_token(token, settings)
    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")
    return UUID(payload["sub"]), UUID(payload["org_id"])


def decode_refresh_token(token: str, settings: Settings) -> UUID:
    """Decode a refresh token and return user_id."""
    payload = decode_token(token, settings)
    if payload.get("type") != "refresh":
        raise AuthenticationError("Invalid token type")
    return UUID(payload["sub"])
