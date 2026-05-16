"""
app/main.py

FastAPI application entry point for the AI Opportunity Intelligence Platform.
Configures CORS, registers routers, sets up logging, and exposes health check.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.utils.logging import setup_logging
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler — runs logging setup before first request."""
    setup_logging()
    
    # Create tables for SQLite/In-memory DB on startup
    if engine and engine.url.drivername == "sqlite":
        Base.metadata.create_all(bind=engine)
        
    yield


app = FastAPI(
    lifespan=lifespan,
    title="AI Opportunity Intelligence Platform",
    description=(
        "Transforms public career page and engineering blog data into "
        "structured commercial opportunity intelligence for IT service companies."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        JSON with status 'ok'.
    """
    return {"status": "ok", "env": settings.app_env}
