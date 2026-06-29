"""Authentication dependencies."""

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decode_access_token
from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationError
from app.db.session import get_db
from app.models import User
from app.repositories.user import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    """Resolve the authenticated user from a Bearer token."""
    if credentials is None:
        raise AuthenticationError("Missing authentication token")
    user_id, org_id = decode_access_token(credentials.credentials, settings)
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if user is None or user.organization_id != org_id:
        raise AuthenticationError("Invalid authentication token")
    request.state.organization_id = str(user.organization_id)
    return user


async def get_user_from_token(
    token: str,
    session: AsyncSession,
    settings: Settings,
) -> User:
    """Resolve a user from a raw JWT (for WebSocket auth)."""
    user_id, org_id = decode_access_token(token, settings)
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if user is None or user.organization_id != org_id:
        raise AuthenticationError("Invalid authentication token")
    return user
