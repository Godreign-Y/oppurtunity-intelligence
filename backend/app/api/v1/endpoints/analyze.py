"""
app/api/v1/endpoints/analyze.py

API endpoint for triggering the full company intelligence analysis pipeline.
Runs career and blog pipelines, then applies AI inference.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.signal import AnalyzeCompanyRequest, AIOpportunityOutput
from app.services.career.pipeline import run_career_pipeline
from app.services.blog.pipeline import run_blog_pipeline
from app.services.ai.inference import run_ai_inference
from app.services.company_service import (
    get_or_create_company,
    update_company_ats,
    update_company_blog,
    save_signals,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", summary="Trigger full company intelligence analysis")
async def analyze_company(
    request: AnalyzeCompanyRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Run the complete intelligence pipeline for a company.

    Steps:
      1. Career page pipeline (ATS discovery → job extraction → signal normalization)
      2. Engineering blog pipeline (blog discovery → article extraction → signal normalization)
      3. AI inference over all combined signals
      4. Persist results to database

    Args:
        request: Contains company_name.
        db: Injected database session.

    Returns:
        Summary dict with signal counts, ATS info, blog URL, and AI analysis.
    """
    company_name = request.company_name.strip()
    if not company_name:
        raise HTTPException(status_code=400, detail="company_name must not be empty.")

    logger.info(f"[AnalyzeEndpoint] Analyzing: {company_name}")

    company = get_or_create_company(db, company_name)

    import asyncio

    # --- Concurrent Pipeline Execution ---
    career_task = run_career_pipeline(company_name)
    blog_task = run_blog_pipeline(company_name)
    
    (career_signals, ats_platform, ats_url), (blog_signals, blog_url) = await asyncio.gather(career_task, blog_task)

    if ats_platform and ats_url:
        update_company_ats(db, company, ats_platform, ats_url)
    if blog_url:
        update_company_blog(db, company, blog_url)

    all_signals = career_signals + blog_signals
    
    # Prioritize overall signals by confidence and limit to top 10
    all_signals.sort(key=lambda x: x.confidence, reverse=True)
    all_signals = all_signals[:10]

    # --- AI Inference ---
    ai_output: AIOpportunityOutput | None = await run_ai_inference(all_signals, company_name)
    ai_dict = ai_output.model_dump() if ai_output else None

    # --- Persist ---
    saved_records = save_signals(db, company, all_signals, ai_analysis=ai_dict)
    
    # Serialize the ORM objects using the SignalResponse schema to ensure IDs are included
    from app.schemas.signal import SignalResponse
    serialized_signals = [SignalResponse.model_validate(s).model_dump(mode="json") for s in saved_records]

    return {
        "company_name": company_name,
        "ats_platform": ats_platform,
        "ats_url": ats_url,
        "blog_url": blog_url,
        "career_signals_count": len(career_signals),
        "blog_signals_count": len(blog_signals),
        "total_signals": len(all_signals),
        "signals": serialized_signals,  # Include persisted signals with IDs
        "ai_analysis": ai_dict,
    }
