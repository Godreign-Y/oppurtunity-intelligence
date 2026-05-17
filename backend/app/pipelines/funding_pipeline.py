"""
app/pipelines/funding_pipeline.py

Standalone Funding Intelligence Pipeline.

Fetches startup funding rounds from RSS feeds, extracts company/amount/stage
using LLM, validates SaaS classification, and persists to database.

Entry point: run_funding_pipeline(company_name, db)
"""

import logging
from typing import Any
from sqlalchemy.orm import Session

from app.services.funding.service import FundingService, infer_funding_opportunity_category

logger = logging.getLogger(__name__)


def _infer_category_from_funding(stage: str | None, amount: float | None) -> str:
    """
    Infer the opportunity category from a funding round stage and amount.

    Newly funded companies in early stages typically need cloud infrastructure.
    Series B/C companies often need DevOps modernization or AI capabilities.
    Large rounds often indicate AI or ML scaling initiatives.

    Args:
        stage: Funding stage string (Seed, Series A, B, C, etc.)
        amount: Funding amount in millions.

    Returns:
        A canonical opportunity category string.
    """
    return infer_funding_opportunity_category(stage, amount)


async def run_funding_pipeline(
    company_name: str,
    db: Session,
) -> list[dict[str, Any]]:
    """
    Run the Funding Intelligence Pipeline.

    Runs the FundingService pipeline, then enriches results with
    opportunity categories from the 6 canonical categories.

    Args:
        company_name: Company context (used for logging — funding runs globally).
        db: Active SQLAlchemy database session.

    Returns:
        List of enriched funding event dicts with opportunity_category field.
    """
    logger.info(f"[FundingPipeline] Starting for context: {company_name}")

    try:
        result = await FundingService.run_funding_pipeline(db)
        events = result.get("events", [])
        logger.info(f"[FundingPipeline] Raw result: {result.get('total_ingested', 0)} events ingested")
    except Exception as exc:
        logger.error(f"[FundingPipeline] Failed: {exc}")
        return []

    enriched: list[dict[str, Any]] = []
    for event in events:
        if company_name and company_name.lower() not in (event.get("company_name") or "").lower():
            continue
        category = _infer_category_from_funding(
            event.get("stage"),
            event.get("amount"),
        )
        enriched.append({
            **event,
            "opportunity_category": category,
            "source": "funding",
        })

    logger.info(f"[FundingPipeline] Completed: {len(enriched)} enriched events")
    return enriched
