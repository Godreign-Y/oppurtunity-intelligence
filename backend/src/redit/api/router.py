"""Core API routes (ingestion + intelligence only)."""

from fastapi import APIRouter

from redit.api import ingestion, intelligence

api_router = APIRouter()
api_router.include_router(ingestion.router)
api_router.include_router(intelligence.router)
