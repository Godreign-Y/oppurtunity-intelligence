"""
app/api/v1/endpoints/funding.py

FastAPI router for corporate funding signals.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.funding.service import FundingService
from app.schemas.funding import FundingEventResponse, FundingInsightsSchema

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/events", response_model=List[FundingEventResponse])
def get_funding_events(limit: int = 50, db: Session = Depends(get_db)):
    """
    Get recent corporate funding round logs.
    """
    events = FundingService.get_recent_funding_events(db, limit=limit)
    
    # Map company names to responses
    response = []
    for e in events:
        resp = FundingEventResponse.model_validate(e)
        if e.company:
            resp.company_name = e.company.name
        response.append(resp)
        
    return response


@router.post("/ingest")
def trigger_funding_ingestion(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Asynchronously trigger startup funding rounds ingestion (RSS feeds + AI parsing).
    """
    def run_sync():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(FundingService.run_funding_pipeline(db))
        finally:
            loop.close()

    background_tasks.add_task(run_sync)
    return {"message": "Funding intelligence pipeline triggered successfully in the background."}


@router.get("/insights", response_model=FundingInsightsSchema)
def get_funding_insights(db: Session = Depends(get_db)):
    """
    Retrieve aggregated metrics of corporate funding rounds for visualizations.
    """
    events = FundingService.get_recent_funding_events(db, limit=100)
    
    total = 0.0
    valid_amount_count = 0
    stage_counts = {}
    company_amounts = {}
    
    for e in events:
        if e.amount:
            total += e.amount
            valid_amount_count += 1
            company_name = e.company.name if e.company else "Unknown Company"
            company_amounts[company_name] = company_amounts.get(company_name, 0.0) + e.amount
            
        stage = e.stage or "Seed"
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
    avg = total / valid_amount_count if valid_amount_count > 0 else 0.0
    
    stage_dist = [{"stage": k, "count": v} for k, v in stage_counts.items()]
    top_funded = [{"company_name": k, "amount": v} for k, v in sorted(company_amounts.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    # If no data exists, supply default metrics for initial bootstrap
    if not stage_dist:
        stage_dist = [{"stage": "Seed", "count": 0}, {"stage": "Series A", "count": 0}]
    if not top_funded:
        top_funded = []

    return {
        "total_funding": round(total, 2),
        "average_funding": round(avg, 2),
        "events_count": len(events),
        "stage_distribution": stage_dist,
        "top_funded": top_funded
    }
