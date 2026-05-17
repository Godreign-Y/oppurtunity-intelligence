"""
app/pipelines/blog_pipeline.py

Standalone Engineering Blog Intelligence Pipeline.

Wraps the existing blog scraping service and enriches signals with
the 6 canonical opportunity categories before returning results.

Entry point: run_blog_pipeline_enriched(company_name)
"""

import logging
from typing import Any

from app.services.blog.pipeline import run_blog_pipeline
from app.schemas.signal import UnifiedSignalSchema
from app.config.category_mapper import map_pain_list_to_category

logger = logging.getLogger(__name__)


async def run_blog_pipeline_enriched(
    company_name: str,
) -> tuple[list[UnifiedSignalSchema], str | None]:
    """
    Run the Engineering Blog Intelligence Pipeline for a specific company.

    Wraps run_blog_pipeline and ensures each signal has an opportunity_category.

    Args:
        company_name: Target company to scrape engineering blog for.

    Returns:
        Tuple of (signals_list, blog_url).
        Each signal has an opportunity_category based on its pain_indicators.
    """
    logger.info(f"[BlogPipeline] Starting for company: {company_name}")

    try:
        signals, blog_url = await run_blog_pipeline(company_name)
        logger.info(f"[BlogPipeline] Fetched {len(signals)} blog signals from {blog_url}")
    except Exception as exc:
        logger.error(f"[BlogPipeline] Failed: {exc}")
        return [], None

    # Enrich each signal with an opportunity category
    for signal in signals:
        category = map_pain_list_to_category(signal.pain_indicators or [])
        signal.opportunity_category = category

    logger.info(
        f"[BlogPipeline] Completed: {len(signals)} signals, blog_url={blog_url}"
    )
    return signals, blog_url
