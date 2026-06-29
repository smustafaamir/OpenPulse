"""Authentication service."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.core.config import Settings
from app.core.exceptions import AuthenticationError, ConflictError
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)


class AuthService:
    """Handle registration, login, and token refresh."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._users = UserRepository(session)
        self._orgs = OrganizationRepository(session)

    async def register(self, data: RegisterRequest) -> TokenResponse:
        """Create organization and user, return tokens."""
        existing = await self._users.get_by_email(data.email)
        if existing is not None:
            raise ConflictError("Email already registered")
        org = await self._orgs.create(data.organization_name)
        user = await self._users.create(
            email=data.email,
            password_hash=hash_password(data.password),
            organization_id=org.id,
        )
        return self._build_tokens(user.id, user.organization_id)

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate user and return tokens."""
        user = await self._users.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.password_hash):
            raise AuthenticationError("Invalid email or password")
        return self._build_tokens(user.id, user.organization_id)

    async def refresh(self, data: RefreshRequest) -> TokenResponse:
        """Issue a new access token from a refresh token."""
        user_id = decode_refresh_token(data.refresh_token, self._settings)
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise AuthenticationError("Invalid refresh token")
        access_token = create_access_token(
            user.id, user.organization_id, self._settings
        )
        return TokenResponse(access_token=access_token)

    def _build_tokens(self, user_id: UUID, organization_id: UUID) -> TokenResponse:
        """Create access and refresh tokens."""
        return TokenResponse(
            access_token=create_access_token(user_id, organization_id, self._settings),
            refresh_token=create_refresh_token(user_id, self._settings),
        )
