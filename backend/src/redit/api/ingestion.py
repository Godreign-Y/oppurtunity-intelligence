"""Ingestion endpoint — global Reddit discovery → pipeline."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from redit.api.deps import get_ingestion_service
from redit.models.pipeline import IngestionRequest, IngestionResponse
from redit.services.ingestion_service import IngestionService

router = APIRouter(tags=["ingestion"])


@router.post(
    "/ingestion",
    response_model=IngestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest global Reddit feeds and run the filtering pipeline",
)
async def ingest(
    request: IngestionRequest,
    service: Annotated[IngestionService, Depends(get_ingestion_service)],
) -> IngestionResponse:
    """
    Fetch r/all, r/popular, and optional search results; process one post at a time.

    Only validated high-signal intelligence JSON is stored.
    """
    try:
        return await service.ingest(request)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ingestion failed: {exc}",
        ) from exc
