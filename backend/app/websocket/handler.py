"""WebSocket event stream handler."""

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.auth.dependencies import get_user_from_token
from app.core.config import get_settings
from app.core.exceptions import AuthenticationError
from app.db.session import get_session_factory
from app.websocket.manager import ConnectionManager

router = APIRouter()


def create_events_ws_router(connection_manager: ConnectionManager) -> APIRouter:
    """Create WebSocket router with injected connection manager."""

    @router.websocket("/ws/events")
    async def events_websocket(
        websocket: WebSocket,
        token: str = Query(...),
    ) -> None:
        """Stream live events for the authenticated user's organization."""
        settings = get_settings()
        session_factory = get_session_factory()
        async with session_factory() as session:
            try:
                user = await get_user_from_token(token, session, settings)
            except AuthenticationError:
                await websocket.close(code=1008)
                return
            org_id = user.organization_id

        await connection_manager.connect(websocket, org_id)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await connection_manager.disconnect(websocket, org_id)

    return router
