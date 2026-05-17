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
from app.config.category_mapper import map_pain_list_to_category, map_to_opportunity_category

logger = logging.getLogger(__name__)


def get_or_create_company(db: Session, name: str, domain: Optional[str] = None) -> Company:
    """
    Retrieve an existing company by name (case-insensitive) or create a new record.
    Company names are stored in Title Case for consistency.

    Args:
        db: SQLAlchemy database session.
        name: Company name (any case).
        domain: Optional company domain.

    Returns:
        Company ORM instance.
    """
    # Normalize to Title Case, strip whitespace
    normalized_name = name.strip().title()

    # Case-insensitive lookup to prevent duplicates ("spotify" vs "Spotify")
    company = (
        db.query(Company)
        .filter(Company.name.ilike(normalized_name))
        .first()
    )
    if not company:
        company = Company(name=normalized_name, domain=domain)
        db.add(company)
        db.commit()
        db.refresh(company)
        logger.info(f"[CompanyService] Created company: {normalized_name}")
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
            opportunity_category=s.opportunity_category
            or map_pain_list_to_category(s.pain_indicators or []),
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
    Retrieve all signals for a company by name (case-insensitive).

    Args:
        db: SQLAlchemy database session.
        company_name: Company name to look up.

    Returns:
        List of Signal ORM instances.
    """
    company = db.query(Company).filter(Company.name.ilike(company_name.strip())).first()
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
    Accepts both dict and Pydantic model instances.

    Args:
        db: SQLAlchemy database session.
        company: Company ORM instance.
        signals: List of MarketPainSignalSchema instances or dicts.

    Returns:
        List of persisted MarketPainSignal ORM instances.
    """
    from app.models.market_pain import MarketPainSignal

    def _get(signal: any, key: str, default: any = None) -> any:
        """Dict-safe getter for both dict and Pydantic model instances."""
        if isinstance(signal, dict):
            return signal.get(key, default)
        return getattr(signal, key, default)

    saved = []
    for s in signals:
        ts = None
        timestamp = _get(s, "timestamp")
        if timestamp:
            try:
                ts = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        pain_category = _get(s, "pain_category")
        opportunity_category = _get(s, "opportunity_category")
        if not opportunity_category:
            opportunity_category = map_to_opportunity_category(pain_category or "enterprise_reliability")

        record = MarketPainSignal(
            company_id=company.id,
            source=_get(s, "source", "reddit"),
            post_id=_get(s, "post_id"),
            subreddit=_get(s, "subreddit"),
            title=_get(s, "title"),
            body=_get(s, "body"),
            url=_get(s, "url"),
            author=_get(s, "author"),
            upvotes=_get(s, "upvotes", 0),
            num_comments=_get(s, "num_comments", 0),
            product=_get(s, "product"),
            company_name_detected=_get(s, "company"),
            technologies=_get(s, "technologies", []),
            workflows=_get(s, "workflows", []),
            pain_category=pain_category,
            opportunity_category=opportunity_category,
            pain_subcategories=_get(s, "pain_subcategories", []),
            workflow_pains=_get(s, "workflow_pains", []),
            severity=_get(s, "severity", "low"),
            tech_confidence=_get(s, "tech_confidence", 0.0),
            sentiment_score=_get(s, "sentiment_score", 0.0),
            business_relevance=_get(s, "business_relevance", 0.0),
            momentum_score=_get(s, "momentum_score", 0.0),
            strategic_fit_score=_get(s, "strategic_fit_score", 0.0),
            confidence=_get(s, "confidence", 0.0),
            capability_matches=_get(s, "capability_matches", []),
            matched_practices=_get(s, "matched_practices", []),
            matched_accelerators=_get(s, "matched_accelerators", []),
            timestamp=ts,
        )
        db.add(record)
        saved.append(record)

    db.commit()
    logger.info(f"[CompanyService] Saved {len(saved)} market pain signals for: {company.name}")
    return saved


def get_company_market_pain_signals(db: Session, company_name: str) -> list:
    """
    Retrieve all market pain signals for a company by name (case-insensitive).

    Args:
        db: SQLAlchemy database session.
        company_name: Company name.

    Returns:
        List of MarketPainSignal ORM instances.
    """
    company = db.query(Company).filter(Company.name.ilike(company_name.strip())).first()
    if not company:
        return []
    return company.market_pain_signals
