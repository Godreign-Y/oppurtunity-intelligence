"""
app/api/v1/endpoints/signals.py

API endpoints for retrieving persisted intelligence signals.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.signal import SignalResponse
from app.services.company_service import get_company_signals, list_companies
from app.schemas.company import CompanyResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/companies", response_model=list[CompanyResponse], summary="List tracked companies")
def get_companies(db: Session = Depends(get_db)) -> list:
    """
    Return all companies currently tracked in the platform.

    Args:
        db: Injected database session.

    Returns:
        List of CompanyResponse objects.
    """
    return list_companies(db)


@router.get(
    "/companies/{company_name}/signals",
    response_model=list[SignalResponse],
    summary="Get signals for a company",
)
def get_signals_for_company(
    company_name: str,
    db: Session = Depends(get_db),
) -> list:
    """
    Return all intelligence signals for the specified company.

    Args:
        company_name: URL path parameter for company name.
        db: Injected database session.

    Returns:
        List of SignalResponse objects.

    Returns an empty list if the company has no recorded signals.
    """
    signals = get_company_signals(db, company_name)
    return signals


@router.get(
    "/companies/{company_name}/market_pain",
    summary="Get market pain signals for a company",
)
def get_market_pain_for_company(
    company_name: str,
    db: Session = Depends(get_db),
) -> list:
    """
    Return all market pain signals for the specified company.
    """
    from app.services.company_service import get_company_market_pain_signals
    signals = get_company_market_pain_signals(db, company_name)
    
    # Serialize for response
    return [
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
            "opportunity_category": r.opportunity_category,
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
        for r in signals
    ]
