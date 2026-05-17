"""Relanto relevance scoring and opportunity aggregation."""

from collections import Counter
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.models.company import Company
from app.models.funding_event import FundingEvent
from app.models.github_signal import GitHubSignal
from app.models.hiring_signal import HiringSignal
from app.models.market_pain import MarketPainSignal
from app.models.service_intelligence import (
    RelantoOpportunityScore,
    ServiceCompany,
    ServiceOpportunity,
    ServicePastDeal,
)
from app.models.signal import Signal
from app.services.service_intelligence.relanto_seed import seed_relanto


def _code_for_category(category: str | None) -> str:
    mapping = {
        "AI Infrastructure": "OPP_AI_INFRA",
        "Cloud Migration": "OPP_CLOUD_MIGRATION",
        "DevOps Modernization": "OPP_DEVOPS",
        "MLOps Scaling": "OPP_MLOPS",
        "Legacy Refactoring": "OPP_LEGACY",
        "Cost Optimization": "OPP_COST_OPT",
    }
    return mapping.get(category or "", "OPP_DEVOPS")


def _signal_to_dict(company_name: str, signal: Any, source: str) -> dict:
    if isinstance(signal, Signal):
        title = signal.role_title or signal.event_type or signal.source_type
        body = " ".join(signal.evidence or []) or " ".join(signal.business_implications or [])
        return {
            "id": str(signal.id),
            "company_name": company_name,
            "source": signal.source_type,
            "title": title,
            "body": body,
            "source_url": signal.source_url,
            "opportunity_category": signal.opportunity_category,
            "confidence": signal.confidence,
            "technologies": signal.technologies or [],
            "pain_indicators": signal.pain_indicators or [],
        }
    if isinstance(signal, MarketPainSignal):
        return {
            "id": str(signal.id),
            "company_name": company_name,
            "source": signal.source,
            "title": signal.title,
            "body": signal.body,
            "source_url": signal.url,
            "opportunity_category": signal.opportunity_category,
            "confidence": signal.confidence,
            "technologies": signal.technologies or [],
            "pain_indicators": [signal.pain_category] + (signal.pain_subcategories or []),
        }
    if isinstance(signal, HiringSignal):
        return {
            "id": str(signal.id),
            "company_name": company_name,
            "source": "hiring_signals",
            "title": signal.job_title,
            "body": signal.sanitized_description,
            "source_url": signal.source_url,
            "opportunity_category": signal.opportunity_category,
            "confidence": 0.72,
            "technologies": signal.detected_tech_stack or [],
            "pain_indicators": [],
        }
    if isinstance(signal, FundingEvent):
        return {
            "id": str(signal.id),
            "company_name": company_name,
            "source": "funding",
            "title": f"{company_name} {signal.stage or 'Funding'}",
            "body": signal.raw_text,
            "source_url": signal.source_url,
            "opportunity_category": signal.opportunity_category,
            "confidence": min(0.95, (signal.opportunity_score or 10) / 50),
            "technologies": [],
            "pain_indicators": [signal.stage] if signal.stage else [],
        }
    if isinstance(signal, GitHubSignal):
        metadata = signal.metadata_json or {}
        return {
            "id": str(signal.id),
            "company_name": metadata.get("org") or company_name,
            "source": "github_issues",
            "title": signal.title,
            "body": signal.content,
            "source_url": signal.source_url,
            "opportunity_category": signal.opportunity_category,
            "confidence": 0.68,
            "technologies": [],
            "pain_indicators": metadata.get("labels", []),
        }
    return {}


def _score_relanto_fit(db: Session, service_company: ServiceCompany, category: str | None, technologies: list[str]) -> dict:
    opportunity = db.query(ServiceOpportunity).filter(
        ServiceOpportunity.opportunity_code == _code_for_category(category)
    ).first()
    if not opportunity:
        return {"relanto_relevance_score": 50, "practices": [], "past_deals": [], "reason": "Default service fit."}

    mappings = opportunity.practice_mappings or []
    practices = []
    mapping_score = 0
    for mapping in mappings:
        practice = mapping.practice
        practices.append({
            "practice_name": practice.practice_name,
            "practice_code": practice.practice_code,
            "relevance_score": mapping.relevance_score,
            "delivery_strength": practice.delivery_strength,
            "sme_count": practice.sme_count,
            "description": practice.description,
        })
        mapping_score += mapping.relevance_score

    avg_mapping = mapping_score / len(mappings) if mappings else 6
    deals = db.query(ServicePastDeal).filter(
        ServicePastDeal.company_id == service_company.id,
        ServicePastDeal.opportunity_type == opportunity.opportunity_name,
    ).all()
    deal_bonus = min(12, len(deals) * 6)

    tech_text = " ".join(technologies).lower()
    practice_text = " ".join(p["description"] or "" for p in practices).lower()
    tech_overlap = sum(1 for tech in technologies if tech.lower() in practice_text or tech.lower() in tech_text)
    tech_bonus = min(10, tech_overlap * 2)

    score = round(min(99, 45 + avg_mapping * 4 + deal_bonus + tech_bonus))
    reason = f"{opportunity.opportunity_name} maps to {len(practices)} Relanto practice(s), with {len(deals)} similar past deal(s)."

    return {
        "relanto_relevance_score": score,
        "practices": practices,
        "past_deals": [
            {
                "client_name": deal.client_name,
                "project_name": deal.project_name,
                "technologies_used": deal.technologies_used or [],
                "transformation_outcome": deal.transformation_outcome,
                "client_satisfaction_score": deal.client_satisfaction_score,
            }
            for deal in deals
        ],
        "reason": reason,
    }


def _priority_for_confidence(confidence: float) -> str:
    return "High" if confidence >= 0.8 else "Medium" if confidence >= 0.6 else "Low"


def _score_row_to_dict(row: RelantoOpportunityScore) -> dict:
    return {
        "id": row.source_id,
        "company_name": row.company_name,
        "source": row.source,
        "title": row.title,
        "body": row.body,
        "source_url": row.source_url,
        "opportunity_category": row.opportunity_category,
        "confidence": float(row.confidence or 0),
        "technologies": row.technologies or [],
        "pain_indicators": row.pain_indicators or [],
        "score": row.score,
        "priority": row.priority,
        "relanto_relevance_score": row.relanto_relevance_score,
        "practices": row.practices or [],
        "past_deals": row.past_deals or [],
        "reason": row.reason,
    }


def _upsert_score(db: Session, item: dict, fit: dict) -> RelantoOpportunityScore:
    confidence = float(item.get("confidence") or 0.6)
    score = round(min(99, confidence * 100))
    row = db.query(RelantoOpportunityScore).filter(
        RelantoOpportunityScore.source == item["source"],
        RelantoOpportunityScore.source_id == item["id"],
    ).first()
    if not row:
        row = RelantoOpportunityScore(source=item["source"], source_id=item["id"])
        db.add(row)

    row.company_name = item["company_name"]
    row.title = item.get("title")
    row.body = item.get("body")
    row.source_url = item.get("source_url")
    row.opportunity_category = item.get("opportunity_category")
    row.confidence = confidence
    row.score = score
    row.priority = _priority_for_confidence(confidence)
    row.relanto_relevance_score = fit["relanto_relevance_score"]
    row.practices = fit.get("practices") or []
    row.past_deals = fit.get("past_deals") or []
    row.reason = fit.get("reason")
    row.technologies = item.get("technologies") or []
    row.pain_indicators = item.get("pain_indicators") or []
    return row


def refresh_relanto_opportunity_scores(db: Session, company_name: str | None = None) -> int:
    """Rebuild persisted Relanto fit rows from current source signals."""
    relanto = seed_relanto(db)
    fit_cache: dict[tuple[str | None, tuple[str, ...]], dict] = {}

    def score_fit(category: str | None, technologies: list[str]) -> dict:
        key = (category, tuple(sorted(t.lower() for t in technologies)))
        if key not in fit_cache:
            fit_cache[key] = _score_relanto_fit(db, relanto, category, technologies)
        return fit_cache[key]

    companies_query = db.query(Company).options(
        selectinload(Company.signals),
        selectinload(Company.market_pain_signals),
        selectinload(Company.hiring_signals),
        selectinload(Company.funding_events),
    )
    if company_name:
        companies_query = companies_query.filter(Company.name.ilike(f"%{company_name}%"))
    companies = companies_query.order_by(Company.created_at.desc()).limit(8).all()

    rows_written = 0
    for company in companies:
        source_rows: list[tuple[Any, str]] = []
        source_rows.extend((s, "signal") for s in company.signals)
        source_rows.extend((s, "market_pain") for s in company.market_pain_signals)
        source_rows.extend((s, "hiring") for s in company.hiring_signals)
        source_rows.extend((s, "funding") for s in company.funding_events)

        for raw, source in source_rows:
            item = _signal_to_dict(company.name, raw, source)
            if not item:
                continue
            fit = score_fit(item.get("opportunity_category"), item.get("technologies") or [])
            _upsert_score(db, item, fit)
            rows_written += 1

    # Include recent GitHub org signals that may not be linked to Company rows.
    github_rows = db.query(GitHubSignal).order_by(GitHubSignal.created_at.desc()).limit(50).all()
    for raw in github_rows:
        org_name = (raw.metadata_json or {}).get("org") or "Unknown"
        if company_name and company_name.lower() not in org_name.lower():
            continue
        item = _signal_to_dict(org_name, raw, "github")
        fit = score_fit(item.get("opportunity_category"), item.get("technologies") or [])
        _upsert_score(db, item, fit)
        rows_written += 1

    db.commit()
    return rows_written


def list_relanto_opportunities(
    db: Session,
    company_name: str | None = None,
    practice_code: str | None = None,
    refresh: bool = False,
) -> list[dict]:
    seed_relanto(db)
    query = db.query(RelantoOpportunityScore)
    if company_name:
        query = query.filter(RelantoOpportunityScore.company_name.ilike(f"%{company_name}%"))

    if refresh or query.count() == 0:
        refresh_relanto_opportunity_scores(db, company_name=company_name)
        query = db.query(RelantoOpportunityScore)
        if company_name:
            query = query.filter(RelantoOpportunityScore.company_name.ilike(f"%{company_name}%"))

    rows = query.order_by(
        RelantoOpportunityScore.relanto_relevance_score.desc(),
        RelantoOpportunityScore.score.desc(),
    ).limit(250).all()

    opportunities = [_score_row_to_dict(row) for row in rows]
    if practice_code:
        opportunities = [
            item for item in opportunities
            if any(p.get("practice_code") == practice_code for p in item.get("practices") or [])
        ]
    return opportunities


def list_practices(db: Session) -> list[dict]:
    relanto = seed_relanto(db)
    return [
        {
            "practice_name": p.practice_name,
            "practice_code": p.practice_code,
            "practice_category": p.practice_category,
            "description": p.description,
            "delivery_strength": p.delivery_strength,
            "sme_count": p.sme_count,
            "growth_priority": p.growth_priority,
        }
        for p in sorted(relanto.practices, key=lambda practice: practice.practice_name)
    ]
