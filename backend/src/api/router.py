"""API route composition."""

from fastapi import APIRouter

from api.routes import cases, documents, health, profiles

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(cases.router)
api_router.include_router(profiles.router)
api_router.include_router(documents.router)
api_router.include_router(health.router)