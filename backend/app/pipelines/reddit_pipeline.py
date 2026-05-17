"""
app/pipelines/reddit_pipeline.py

Standalone Reddit / F5Bot Market Pain Intelligence Pipeline.

Wraps the existing market_pain pipeline and enriches each signal
with one of the 6 canonical opportunity categories.

Entry point: run_reddit_pipeline(company_name)
"""

import logging

from app.services.market_pain.pipeline import run_market_pain_pipeline
from app.services.market_pain.schemas import MarketPainSignalSchema
from app.config.category_mapper import map_to_opportunity_category

logger = logging.getLogger(__name__)


def _infer_category_from_pain_signal(signal: MarketPainSignalSchema) -> str:
    """
    Map a MarketPainSignalSchema's pain category to a canonical opportunity category.

    Uses the pain_category as the primary signal, falls back to subcategories.

    Args:
        signal: A scored MarketPainSignalSchema from the market pain pipeline.

    Returns:
        A canonical opportunity category string.
    """
    if signal.pain_category:
        return map_to_opportunity_category(signal.pain_category)

    if signal.pain_subcategories:
        return map_to_opportunity_category(signal.pain_subcategories[0])

    return map_to_opportunity_category("enterprise_reliability")


async def run_reddit_pipeline(
    company_name: str,
    subreddits: list[str] | None = None,
) -> list[MarketPainSignalSchema]:
    """
    Run the Reddit / F5Bot Market Pain Intelligence Pipeline.

    Fetches and scores community pain signals, then assigns each signal
    to one of the 6 canonical opportunity categories.

    Args:
        company_name: Company context for the pipeline run.
        subreddits: Optional override of subreddits to scan.

    Returns:
        List of enriched market pain signal objects with opportunity_category.
    """
    logger.info(f"[RedditPipeline] Starting for company: {company_name}")

    try:
        signals: list[MarketPainSignalSchema] = await run_market_pain_pipeline(
            company_name=company_name,
            subreddits=subreddits,
        )
        logger.info(f"[RedditPipeline] Received {len(signals)} pain signals")
    except Exception as exc:
        logger.error(f"[RedditPipeline] Market pain pipeline failed: {exc}")
        return []

    enriched: list[MarketPainSignalSchema] = []
    for signal in signals:
        category = _infer_category_from_pain_signal(signal)
        signal.opportunity_category = category
        enriched.append(signal)

    logger.info(
        f"[RedditPipeline] Completed: {len(enriched)} signals with categories"
    )
    return enriched
