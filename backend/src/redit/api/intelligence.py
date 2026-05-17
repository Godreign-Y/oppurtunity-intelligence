"""Intelligence retrieval and export endpoint."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, Response

from redit.api.deps import get_intelligence_service
from redit.services.intelligence_service import IntelligenceService

router = APIRouter(tags=["intelligence"])


@router.get(
    "/intelligence/{run_id}",
    response_model=None,
    summary="Get or export validated intelligence JSON for a run",
)
async def get_intelligence(
    run_id: UUID,
    service: Annotated[IntelligenceService, Depends(get_intelligence_service)],
    export: bool = Query(
        default=False,
        description="When true, return downloadable JSON attachment.",
    ),
) -> Response:
    """Return intelligence records; set export=true for file download."""
    if export:
        payload = await service.export_records(run_id)
        if payload is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
        return JSONResponse(
            content=payload,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="intelligence-{run_id}.json"',
            },
        )

    records = await service.get_records(run_id)
    if records is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return JSONResponse(
        content=[r.model_dump(mode="json") for r in records],
        media_type="application/json",
    )
