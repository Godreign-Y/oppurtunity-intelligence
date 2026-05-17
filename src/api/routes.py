from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.db.database import get_db
from src.db.crud import get_recent_funding_events
from src.schemas.funding import FundingEventResponse
from src.pipeline.orchestrator import run_pipeline

router = APIRouter(prefix="/api/v1")

@router.get("/funding-events", response_model=List[FundingEventResponse])
async def read_funding_events(limit: int = 50, session: AsyncSession = Depends(get_db)):
    """
    Get recent tracked funding events.
    """
    events = await get_recent_funding_events(session, limit=limit)
    return events

@router.post("/trigger-pipeline")
async def trigger_pipeline(background_tasks: BackgroundTasks):
    """
    Manually trigger the data collection and processing pipeline.
    Runs in the background.
    """
    background_tasks.add_task(run_pipeline)
    return {"message": "Pipeline triggered successfully in the background."}
