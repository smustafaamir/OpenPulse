"""OpenPulse FastAPI application entry point."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import setup_logging
from app.core.middleware import (
    RequestContextMiddleware,
    app_error_handler,
    internal_error_handler,
    validation_error_handler,
)
from app.db.seed import seed_default_organization
from app.websocket.handler import create_events_ws_router
from app.websocket.manager import ConnectionManager
from app.workers.collector_loop import start_collector_task

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application startup and shutdown."""
    settings = get_settings()
    setup_logging(settings.log_level)
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    connection_manager = ConnectionManager(redis)
    app.state.redis = redis
    app.state.connection_manager = connection_manager

    app.include_router(create_events_ws_router(connection_manager))

    await seed_default_organization()
    collector_task = start_collector_task(redis)

    yield

    collector_task.cancel()
    with suppress(Exception):
        await collector_task
    await redis.aclose()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title="OpenPulse",
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, internal_error_handler)

    app.include_router(api_router)
    return app


app = create_app()
