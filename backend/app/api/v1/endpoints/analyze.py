"""
app/api/v1/endpoints/analyze.py

API endpoint for triggering the full company intelligence analysis pipeline.
Runs career, blog, and market pain pipelines, then applies AI inference.
"""

import logging
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.signal import AnalyzeCompanyRequest, AIOpportunityOutput
from app.services.career.pipeline import run_career_pipeline
from app.services.blog.pipeline import run_blog_pipeline
from app.services.market_pain.pipeline import run_market_pain_pipeline
from app.services.ai.inference import run_ai_inference
from app.services.company_service import (
    get_or_create_company,
    update_company_ats,
    update_company_blog,
    save_signals,
    save_market_pain_signals,
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
      3. Market pain pipeline (Reddit → filter → classify → detect → score)
      4. AI inference over all combined signals
      5. Persist results to database

    Args:
        request: Contains company_name.
        db: Injected database session.

    Returns:
        Summary dict with signal counts, ATS info, blog URL, market pain, and AI analysis.
    """
    company_name = request.company_name.strip()
    if not company_name:
        raise HTTPException(status_code=400, detail="company_name must not be empty.")

    logger.info(f"[AnalyzeEndpoint] Analyzing: {company_name}")

    company = get_or_create_company(db, company_name)

    # --- Concurrent Pipeline Execution (all 3 pipelines in parallel) ---
    career_task = run_career_pipeline(company_name)
    blog_task = run_blog_pipeline(company_name)
    market_pain_task = run_market_pain_pipeline(company_name)

    # Graceful degradation: if market pain fails, career+blog still return
    results = await asyncio.gather(
        career_task,
        blog_task,
        market_pain_task,
        return_exceptions=True,
    )

    # Unpack career results
    if isinstance(results[0], Exception):
        logger.error(f"[AnalyzeEndpoint] Career pipeline failed: {results[0]}")
        career_signals, ats_platform, ats_url = [], None, None
    else:
        career_signals, ats_platform, ats_url = results[0]

    # Unpack blog results
    if isinstance(results[1], Exception):
        logger.error(f"[AnalyzeEndpoint] Blog pipeline failed: {results[1]}")
        blog_signals, blog_url = [], None
    else:
        blog_signals, blog_url = results[1]

    # Unpack market pain results
    if isinstance(results[2], Exception):
        logger.error(f"[AnalyzeEndpoint] Market pain pipeline failed: {results[2]}")
        market_pain_signals = []
    else:
        market_pain_signals = results[2]

    if ats_platform and ats_url:
        update_company_ats(db, company, ats_platform, ats_url)
    if blog_url:
        update_company_blog(db, company, blog_url)

    all_signals = career_signals + blog_signals

    # Prioritize overall signals by confidence and limit to top 10
    all_signals.sort(key=lambda x: x.confidence, reverse=True)
    all_signals = all_signals[:10]

    # --- AI Inference (now includes market pain context) ---
    ai_output: AIOpportunityOutput | None = await run_ai_inference(
        all_signals, company_name, market_pain_signals=market_pain_signals
    )
    ai_dict = ai_output.model_dump() if ai_output else None

    # --- Persist career+blog signals ---
    saved_records = save_signals(db, company, all_signals, ai_analysis=ai_dict)

    from app.schemas.signal import SignalResponse
    serialized_signals = [
        SignalResponse.model_validate(s).model_dump(mode="json") for s in saved_records
    ]

    # --- Persist market pain signals ---
    saved_pain_records = []
    if market_pain_signals:
        try:
            saved_pain_records = save_market_pain_signals(db, company, market_pain_signals)
        except Exception as exc:
            logger.error(f"[AnalyzeEndpoint] Market pain persistence failed: {exc}")

    # Serialize market pain signals for response
    serialized_pain = [
        {
            "id": str(r.id),
            "source": r.source,
            "subreddit": r.subreddit,
            "title": r.title,
            "body": r.body[:300] if r.body else "",
            "url": r.url,
            "upvotes": r.upvotes,
            "num_comments": r.num_comments,
            "product": r.product,
            "company": r.company_name_detected,
            "technologies": r.technologies or [],
            "pain_category": r.pain_category,
            "pain_subcategories": r.pain_subcategories or [],
            "workflow_pains": r.workflow_pains or [],
            "severity": r.severity,
            "sentiment_score": r.sentiment_score,
            "momentum_score": r.momentum_score,
            "strategic_fit_score": r.strategic_fit_score,
            "confidence": r.confidence,
            "matched_practices": r.matched_practices or [],
            "matched_accelerators": r.matched_accelerators or [],
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in saved_pain_records
    ]

    return {
        "company_name": company_name,
        "ats_platform": ats_platform,
        "ats_url": ats_url,
        "blog_url": blog_url,
        "career_signals_count": len(career_signals),
        "blog_signals_count": len(blog_signals),
        "market_pain_count": len(market_pain_signals),
        "total_signals": len(all_signals),
        "signals": serialized_signals,
        "market_pain_signals": serialized_pain,
        "ai_analysis": ai_dict,
    }
