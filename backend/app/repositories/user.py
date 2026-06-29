"""User persistence."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class UserRepository:
    """CRUD operations for users."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        email: str,
        password_hash: str,
        organization_id: UUID,
    ) -> User:
        """Insert a new user."""
        user = User(
            email=email,
            password_hash=password_hash,
            organization_id=organization_id,
        )
        self._session.add(user)
        await self._session.flush()
        return user

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email."""
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Fetch a user by ID."""
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
