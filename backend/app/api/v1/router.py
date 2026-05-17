"""
app/api/v1/router.py

Central router that registers all v1 API endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints.analyze import router as analyze_router
from app.api.v1.endpoints.signals import router as signals_router
from app.api.v1.endpoints.git_issues import router as git_issues_router
from app.api.v1.endpoints.funding import router as funding_router
from app.api.v1.endpoints.hiring import router as hiring_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(analyze_router, tags=["analysis"])
api_router.include_router(signals_router, tags=["signals"])
api_router.include_router(git_issues_router, prefix="/git-issues", tags=["git-issues"])
api_router.include_router(funding_router, prefix="/funding", tags=["funding"])
api_router.include_router(hiring_router, prefix="/hiring", tags=["hiring"])
