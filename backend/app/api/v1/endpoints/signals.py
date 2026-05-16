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

    Raises:
        HTTPException 404 if the company has no recorded signals.
    """
    signals = get_company_signals(db, company_name)
    if not signals:
        raise HTTPException(
            status_code=404,
            detail=f"No signals found for company: {company_name}",
        )
    return signals
