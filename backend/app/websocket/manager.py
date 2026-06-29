"""WebSocket connection management."""

import asyncio
import json
import logging
from uuid import UUID

from fastapi import WebSocket
from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from app.services.broadcast import BroadcastService

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections and Redis subscriptions per organization."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis
        self._connections: dict[UUID, set[WebSocket]] = {}
        self._pubsubs: dict[UUID, PubSub] = {}
        self._listener_tasks: dict[UUID, asyncio.Task[None]] = {}

    async def connect(self, websocket: WebSocket, organization_id: UUID) -> None:
        """Accept a WebSocket and subscribe to the org event channel."""
        await websocket.accept()
        if organization_id not in self._connections:
            self._connections[organization_id] = set()
            pubsub = self._redis.pubsub()
            await pubsub.subscribe(BroadcastService.channel_for_org(organization_id))
            self._pubsubs[organization_id] = pubsub
            self._listener_tasks[organization_id] = asyncio.create_task(
                self._listen(organization_id, pubsub)
            )
        self._connections[organization_id].add(websocket)

    async def disconnect(self, websocket: WebSocket, organization_id: UUID) -> None:
        """Remove a WebSocket and clean up when no clients remain."""
        connections = self._connections.get(organization_id)
        if connections is None:
            return
        connections.discard(websocket)
        if not connections:
            task = self._listener_tasks.pop(organization_id, None)
            if task is not None:
                task.cancel()
            pubsub = self._pubsubs.pop(organization_id, None)
            if pubsub is not None:
                await pubsub.unsubscribe()
                await pubsub.close()
            self._connections.pop(organization_id, None)

    async def _listen(self, organization_id: UUID, pubsub: PubSub) -> None:
        """Forward Redis messages to all connected clients for an org."""
        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode()
                await self._broadcast_to_org(organization_id, str(data))
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("Redis listener error for org %s", organization_id)

    async def _broadcast_to_org(self, organization_id: UUID, message: str) -> None:
        """Send a message to all WebSocket clients for an organization."""
        connections = self._connections.get(organization_id, set())
        dead: list[WebSocket] = []
        for websocket in connections:
            try:
                payload = json.loads(message)
                await websocket.send_json(payload)
            except Exception:
                dead.append(websocket)
        for websocket in dead:
            await self.disconnect(websocket, organization_id)
