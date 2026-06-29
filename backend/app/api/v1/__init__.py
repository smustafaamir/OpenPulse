"""API v1 route modules."""

from fastapi import APIRouter

from app.api.v1 import auth, dashboards, events, health, organization

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(organization.router)
api_router.include_router(events.router)
api_router.include_router(dashboards.router)
