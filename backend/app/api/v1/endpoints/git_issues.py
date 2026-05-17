"""
app/api/v1/endpoints/git_issues.py

API endpoints for triggering ingestion and analysis of Git/GitHub issues and Hugging Face models,
and generating/retrieving normalized intelligence signals and enterprise insights.
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.services.github.service import GitHubIngestionService
from app.services.huggingface.service import HuggingFaceIngestionService
from app.services.normalization.service import NormalizationService
from app.services.insights.service import InsightService

router = APIRouter()
logger = logging.getLogger(__name__)

# Request schemas
class IngestRequest(BaseModel):
    query: Optional[str] = None
    queries: Optional[List[str]] = None

@router.post("/ingest", summary="Ingest GitHub Issues & Normalize Signals")
async def ingest_github_issues(
    request: IngestRequest,
    db: Session = Depends(get_db)
):
    """
    Ingest GitHub issues matching a specific query or list of queries,
    and then run the normalization pipeline on all ingested signals.
    """
    try:
        queries_to_run = []
        if request.query:
            queries_to_run.append(request.query)
        if request.queries:
            queries_to_run.extend(request.queries)
            
        if not queries_to_run:
            # Fallback to defaults if nothing passed
            queries_to_run = [
                "deployment failed",
                "rollback issue",
                "latency issue",
                "outage"
            ]
            
        ingestion_service = GitHubIngestionService(db)
        total_ingested = 0
        
        for q in queries_to_run:
            logger.info(f"[GitIssuesAPI] Ingesting GitHub issues for query: {q}")
            results = await ingestion_service.ingest(q)
            total_ingested += len(results)
            
        # Run Normalization
        logger.info("[GitIssuesAPI] Running normalization service on all ingested signals")
        normalization_service = NormalizationService(db)
        normalization_service.run()
        
        return {
            "status": "success",
            "message": f"Successfully ingested {total_ingested} issues across {len(queries_to_run)} queries and updated normalizations.",
            "queries": queries_to_run,
            "total_ingested": total_ingested
        }
    except Exception as e:
        logger.error(f"[GitIssuesAPI] Ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/huggingface/ingest", summary="Ingest Trending Hugging Face Models")
async def ingest_huggingface_models(
    db: Session = Depends(get_db)
):
    """
    Fetch trending AI/ML models from Hugging Face and store them as raw Hugging Face signals.
    """
    try:
        logger.info("[GitIssuesAPI] Ingesting Hugging Face models")
        hf_service = HuggingFaceIngestionService(db)
        parsed_models = await hf_service.ingest()
        
        return {
            "status": "success",
            "message": f"Successfully ingested {len(parsed_models)} Hugging Face models.",
            "total_ingested": len(parsed_models)
        }
    except Exception as e:
        logger.error(f"[GitIssuesAPI] Hugging Face Ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights", summary="Retrieve aggregated enterprise consulting insights")
def get_git_insights(
    db: Session = Depends(get_db)
):
    """
    Generates high-level enterprise consulting insights:
    - Top signal types
    - Ecosystem distribution
    - Severity distribution
    - Top organizations facing issues
    - High-severity organizations (direct consulting leads)
    """
    try:
        insight_service = InsightService(db)
        return {
            "top_signal_types": insight_service.top_signal_types(),
            "ecosystem_distribution": insight_service.ecosystem_distribution(),
            "severity_distribution": insight_service.severity_distribution(),
            "top_organizations": insight_service.top_orgs(),
            "high_severity_organizations": insight_service.high_severity_orgs()
        }
    except Exception as e:
        logger.error(f"[GitIssuesAPI] Insights retrieval failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals", summary="Retrieve recent GitHub signals")
def get_github_signals(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Retrieve raw GitHub signals, ordered by date.
    """
    try:
        insight_service = InsightService(db)
        return insight_service.recent_github_signals(limit=limit)
    except Exception as e:
        logger.error(f"[GitIssuesAPI] GitHub signals retrieval failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/normalized", summary="Retrieve normalized intelligence signals")
def get_normalized_signals(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Retrieve normalized signals, ordered by confidence.
    """
    try:
        insight_service = InsightService(db)
        return insight_service.normalized_signals_summary(limit=limit)
    except Exception as e:
        logger.error(f"[GitIssuesAPI] Normalized signals retrieval failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
