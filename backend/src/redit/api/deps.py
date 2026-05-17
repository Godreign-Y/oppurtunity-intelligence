"""FastAPI dependency injection."""

from typing import Annotated

from fastapi import Depends, Request

from redit.config.settings import Settings, get_settings
from redit.ml.registry import ModelRegistry
from redit.services.ingestion_service import IngestionService
from redit.services.intelligence_service import IntelligenceService
from redit.storage.base import RunStore


def get_run_store(request: Request) -> RunStore:
    """Return application run store from app state."""
    return request.app.state.run_store


def get_model_registry(request: Request) -> ModelRegistry:
    """Return loaded ML model registry from app state."""
    return request.app.state.models


def get_ingestion_service(
    settings: Annotated[Settings, Depends(get_settings)],
    run_store: Annotated[RunStore, Depends(get_run_store)],
    models: Annotated[ModelRegistry, Depends(get_model_registry)],
) -> IngestionService:
    """Construct ingestion service."""
    return IngestionService(settings=settings, run_store=run_store, models=models)


def get_intelligence_service(
    run_store: Annotated[RunStore, Depends(get_run_store)],
) -> IntelligenceService:
    """Construct intelligence service."""
    return IntelligenceService(run_store=run_store)
