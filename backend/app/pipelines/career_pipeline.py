"""
app/pipelines/career_pipeline.py

Standalone Career Page Intelligence Pipeline.

Wraps the existing career scraping service and enriches signals with
the 6 canonical opportunity categories before returning results.

Entry point: run_career_pipeline_enriched(company_name)
"""

import logging
from typing import Any

from app.services.career.pipeline import run_career_pipeline
from app.schemas.signal import UnifiedSignalSchema
from app.config.category_mapper import map_pain_list_to_category

logger = logging.getLogger(__name__)


async def run_career_pipeline_enriched(
    company_name: str,
) -> tuple[list[UnifiedSignalSchema], str | None, str | None]:
    """
    Run the Career Page Intelligence Pipeline for a specific company.

    Wraps run_career_pipeline and adds opportunity_category to each signal.

    Args:
        company_name: Target company to scrape career pages for.

    Returns:
        Tuple of (signals_list, ats_platform, ats_url).
        Each signal has an opportunity_category attribute set.
    """
    logger.info(f"[CareerPipeline] Starting for company: {company_name}")

    try:
        signals, ats_platform, ats_url = await run_career_pipeline(company_name)
        logger.info(f"[CareerPipeline] Fetched {len(signals)} career signals")
    except Exception as exc:
        logger.error(f"[CareerPipeline] Failed: {exc}")
        return [], None, None

    # Enrich each signal with an opportunity category
    for signal in signals:
        category = map_pain_list_to_category(signal.pain_indicators or [])
        signal.opportunity_category = category

    logger.info(
        f"[CareerPipeline] Completed: {len(signals)} signals, ATS={ats_platform}"
    )
    return signals, ats_platform, ats_url
