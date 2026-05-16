"""
app/api/v1/router.py

Central router that registers all v1 API endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints.analyze import router as analyze_router
from app.api.v1.endpoints.signals import router as signals_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(analyze_router, tags=["analysis"])
api_router.include_router(signals_router, tags=["signals"])
