"""
app/services/company_service.py

CRUD operations for Company and Signal records.
Handles persistence of normalized pipeline results to Neon PostgreSQL.
"""

import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.signal import Signal
from app.schemas.signal import UnifiedSignalSchema
from app.schemas.company import CompanyCreate

logger = logging.getLogger(__name__)


def get_or_create_company(db: Session, name: str, domain: Optional[str] = None) -> Company:
    """
    Retrieve an existing company by name or create a new record.

    Args:
        db: SQLAlchemy database session.
        name: Company name.
        domain: Optional company domain.

    Returns:
        Company ORM instance.
    """
    company = db.query(Company).filter(Company.name == name).first()
    if not company:
        company = Company(name=name, domain=domain)
        db.add(company)
        db.commit()
        db.refresh(company)
        logger.info(f"[CompanyService] Created company: {name}")
    return company


def update_company_ats(
    db: Session, company: Company, ats_platform: str, ats_url: str
) -> Company:
    """
    Update the ATS platform detected for a company.

    Args:
        db: SQLAlchemy database session.
        company: Company ORM instance.
        ats_platform: Detected ATS platform name.
        ats_url: ATS jobs URL.

    Returns:
        Updated Company ORM instance.
    """
    company.ats_platform = ats_platform
    db.commit()
    db.refresh(company)
    return company


def update_company_blog(
    db: Session, company: Company, blog_url: str
) -> Company:
    """
    Update the engineering blog URL for a company.

    Args:
        db: SQLAlchemy database session.
        company: Company ORM instance.
        blog_url: Blog URL string.

    Returns:
        Updated Company ORM instance.
    """
    company.blog_url = blog_url
    db.commit()
    db.refresh(company)
    return company


def save_signals(
    db: Session,
    company: Company,
    signals: list[UnifiedSignalSchema],
    ai_analysis: Optional[dict] = None,
) -> list[Signal]:
    """
    Persist a list of normalized signals to the database.

    Args:
        db: SQLAlchemy database session.
        company: Company ORM instance to associate signals with.
        signals: List of UnifiedSignalSchema instances.
        ai_analysis: Optional AI inference output dict to attach to each signal.

    Returns:
        List of persisted Signal ORM instances.
    """
    saved: list[Signal] = []
    for s in signals:
        ts = None
        if s.timestamp:
            try:
                ts = datetime.fromisoformat(s.timestamp.replace("Z", "+00:00"))
            except (ValueError, TypeError, AttributeError):
                # Try parsing relative times or simple formats if needed, or leave as None
                pass

        record = Signal(
            company_id=company.id,
            source_type=s.source_type,
            event_type=s.event_type,
            technologies=s.technologies,
            topics=s.topics,
            pain_indicators=s.pain_indicators,
            business_implications=s.business_implications,
            opportunity_mapping=s.opportunity_mapping,
            confidence=s.confidence,
            evidence=s.evidence,
            source_url=s.source_url,
            ai_analysis=ai_analysis,
            role_title=s.role_title,
            department=s.department,
            seniority=s.seniority,
            location=s.location,
            urgency=s.urgency,
            timestamp=ts,
        )
        db.add(record)
        saved.append(record)

    db.commit()
    logger.info(f"[CompanyService] Saved {len(saved)} signals for company: {company.name}")
    return saved


def get_company_signals(db: Session, company_name: str) -> list[Signal]:
    """
    Retrieve all signals for a company by name.

    Args:
        db: SQLAlchemy database session.
        company_name: Company name to look up.

    Returns:
        List of Signal ORM instances.
    """
    company = db.query(Company).filter(Company.name == company_name).first()
    if not company:
        return []
    return company.signals


def list_companies(db: Session) -> list[Company]:
    """
    List all tracked companies.

    Args:
        db: SQLAlchemy database session.

    Returns:
        List of Company ORM instances.
    """
    return db.query(Company).order_by(Company.created_at.desc()).all()


def save_market_pain_signals(
    db: Session,
    company: Company,
    signals: list,
) -> list:
    """
    Persist market pain signals to the database.

    Args:
        db: SQLAlchemy database session.
        company: Company ORM instance.
        signals: List of MarketPainSignalSchema instances.

    Returns:
        List of persisted MarketPainSignal ORM instances.
    """
    from app.models.market_pain import MarketPainSignal

    saved = []
    for s in signals:
        ts = None
        if s.timestamp:
            try:
                ts = datetime.fromisoformat(s.timestamp.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        record = MarketPainSignal(
            company_id=company.id,
            source=s.source,
            post_id=s.post_id,
            subreddit=s.subreddit,
            title=s.title,
            body=s.body,
            url=s.url,
            author=s.author,
            upvotes=s.upvotes,
            num_comments=s.num_comments,
            product=s.product,
            company_name_detected=s.company,
            technologies=s.technologies,
            workflows=s.workflows,
            pain_category=s.pain_category,
            pain_subcategories=s.pain_subcategories,
            workflow_pains=s.workflow_pains,
            severity=s.severity,
            tech_confidence=s.tech_confidence,
            sentiment_score=s.sentiment_score,
            business_relevance=s.business_relevance,
            momentum_score=s.momentum_score,
            strategic_fit_score=s.strategic_fit_score,
            confidence=s.confidence,
            capability_matches=s.capability_matches,
            matched_practices=s.matched_practices,
            matched_accelerators=s.matched_accelerators,
            timestamp=ts,
        )
        db.add(record)
        saved.append(record)

    db.commit()
    logger.info(f"[CompanyService] Saved {len(saved)} market pain signals for: {company.name}")
    return saved


def get_company_market_pain_signals(db: Session, company_name: str) -> list:
    """
    Retrieve all market pain signals for a company by name.

    Args:
        db: SQLAlchemy database session.
        company_name: Company name.

    Returns:
        List of MarketPainSignal ORM instances.
    """
    company = db.query(Company).filter(Company.name == company_name).first()
    if not company:
        return []
    return company.market_pain_signals
