"""Event schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventCreate(BaseModel):
    """Event ingestion payload."""

    source: str = Field(min_length=1, max_length=128)
    event_type: str = Field(min_length=1, max_length=128)
    symbol: str = Field(min_length=1, max_length=64)
    timestamp: datetime
    importance: int = Field(ge=1, le=5)
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def ensure_utc_aware(cls, value: datetime) -> datetime:
        """Require timezone-aware timestamps."""
        if value.tzinfo is None:
            msg = "timestamp must be timezone-aware (UTC)"
            raise ValueError(msg)
        return value


class EventResponse(BaseModel):
    """Event details."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    source: str
    event_type: str
    symbol: str
    timestamp: datetime
    importance: int
    payload: dict[str, Any]
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_orm_event(cls, event: object) -> "EventResponse":
        """Build response from ORM event (maps event_metadata)."""
        from app.models import Event

        assert isinstance(event, Event)
        return cls(
            id=event.id,
            organization_id=event.organization_id,
            source=event.source,
            event_type=event.event_type,
            symbol=event.symbol,
            timestamp=event.timestamp,
            importance=event.importance,
            payload=event.payload,
            metadata=event.event_metadata,
            created_at=event.created_at,
        )


class EventListResponse(BaseModel):
    """Paginated event list."""

    items: list[EventResponse]
    total: int
    limit: int
    offset: int
