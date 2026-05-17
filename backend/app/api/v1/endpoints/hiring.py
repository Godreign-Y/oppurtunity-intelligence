"""
app/api/v1/endpoints/hiring.py

FastAPI router for technical corporate hiring signals.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.hiring.service import HiringService
from app.schemas.hiring import HiringSignalResponse, HiringInsightsSchema

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/signals", response_model=List[HiringSignalResponse])
def get_hiring_signals(limit: int = 50, db: Session = Depends(get_db)):
    """
    Get recent technical job openings and modernization signals.
    """
    signals = HiringService.get_recent_hiring_signals(db, limit=limit)
    
    response = []
    for s in signals:
        resp = HiringSignalResponse.model_validate(s)
        if s.company:
            resp.company_name = s.company.name
        response.append(resp)
        
    return response


@router.post("/ingest")
def trigger_hiring_ingestion(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Asynchronously trigger job listing crawling and keyword processing.
    """
    def run_sync():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(HiringService.run_hiring_pipeline(db))
        finally:
            loop.close()

    background_tasks.add_task(run_sync)
    return {"message": "Hiring intelligence pipeline triggered successfully in the background."}


@router.get("/insights", response_model=HiringInsightsSchema)
def get_hiring_insights(db: Session = Depends(get_db)):
    """
    Retrieve aggregated technology stack and recruiting company distributions.
    """
    signals = HiringService.get_recent_hiring_signals(db, limit=100)
    
    skill_counts = {}
    company_counts = {}
    
    for s in signals:
        if s.detected_tech_stack:
            for tech in s.detected_tech_stack:
                skill_counts[tech] = skill_counts.get(tech, 0) + 1
                
        company_name = s.company.name if s.company else "Unknown Company"
        company_counts[company_name] = company_counts.get(company_name, 0) + 1
        
    top_skills = [{"tech": k, "count": v} for k, v in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:6]]
    top_hiring = [{"company_name": k, "count": v} for k, v in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    # If no data exists, supply default metrics for initial bootstrap
    if not top_skills:
        top_skills = [{"tech": "Kubernetes", "count": 0}, {"tech": "Docker", "count": 0}]
    if not top_hiring:
        top_hiring = []

    return {
        "total_jobs": len(signals),
        "top_skills": top_skills,
        "top_hiring": top_hiring
    }
