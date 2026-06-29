"""Redis pub/sub broadcasting."""

import json
from uuid import UUID

from redis.asyncio import Redis

from app.schemas.event import EventResponse


class BroadcastService:
    """Publish events to Redis channels for WebSocket fan-out."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    @staticmethod
    def channel_for_org(organization_id: UUID) -> str:
        """Return the Redis channel name for an organization."""
        return f"events:{organization_id}"

    async def publish_event(self, event: EventResponse) -> None:
        """Publish an event to the organization's channel."""
        message = json.dumps({"type": "event", "data": event.model_dump(mode="json")})
        await self._redis.publish(self.channel_for_org(event.organization_id), message)
