"""
app/services/market_pain/pipeline.py

Main orchestrator for the Market Pain Intelligence Pipeline.
Independently callable — does NOT depend on career or blog pipelines.

Flow:
  1. Reddit ingestion (+ F5Bot when active)
  2. Metadata filtering
  3. Tech relevance classification
  4. Entity extraction
  5. Business validation
  6. Frustration detection
  7. Workflow pain detection
  8. Temporal momentum analysis
  9. Capability mapping
  10. Composite scoring
  11. Top-N selection
"""

import logging
import time
from datetime import datetime, timezone

from app.services.market_pain.reddit_client import fetch_all_subreddits
from app.services.market_pain.f5bot_client import fetch_f5bot_alerts
from app.services.market_pain.subreddit_registry import TARGET_SUBREDDITS, get_domain_weight
from app.services.market_pain.metadata_filters import filter_by_metadata
from app.services.market_pain.relevance_classifier import classify_relevance
from app.services.market_pain.entity_extractor import batch_extract_entities
from app.services.market_pain.business_validation import validate_business_relevance
from app.services.market_pain.frustration_detector import detect_frustration
from app.services.market_pain.workflow_pain_detector import detect_workflow_pain
from app.services.market_pain.temporal_analysis import compute_momentum_scores
from app.services.market_pain.capability_mapper import map_capability
from app.services.market_pain.scoring import score_all_signals
from app.services.market_pain.schemas import MarketPainSignalSchema
from app.services.market_pain.utils import timestamp_from_utc, truncate_text

logger = logging.getLogger(__name__)

# Pipeline configuration
MAX_SIGNALS_OUTPUT: int = 15
POSTS_PER_SUBREDDIT: int = 30  # Keep low for speed


async def run_market_pain_pipeline(
    company_name: str,
    subreddits: list[str] | None = None,
    limit_per_sub: int = POSTS_PER_SUBREDDIT,
    max_output: int = MAX_SIGNALS_OUTPUT,
) -> list[MarketPainSignalSchema]:
    """
    Run the complete Market Pain Intelligence Pipeline.

    This is independently callable and does NOT depend on career or blog pipelines.
    Graceful degradation: if any phase fails, the pipeline continues with partial results.

    Args:
        company_name: Company being analyzed (for context logging).
        subreddits: Override subreddit list (defaults to TARGET_SUBREDDITS).
        limit_per_sub: Max posts per subreddit.
        max_output: Max final signals to return.

    Returns:
        List of scored MarketPainSignalSchema objects, sorted by confidence.
    """
    start = time.time()
    subs = subreddits or TARGET_SUBREDDITS
    logger.info(f"[MarketPainPipeline] Starting for context: {company_name} | {len(subs)} subreddits")

    # ── Phase 1: Data Ingestion ──
    try:
        raw_posts = await fetch_all_subreddits(subs, limit_per_sub=limit_per_sub, query=company_name)
        f5bot_posts = await fetch_f5bot_alerts(keywords=[company_name])
        raw_posts.extend(f5bot_posts)
        logger.info(f"[MarketPainPipeline] Phase 1 complete: {len(raw_posts)} raw posts ingested")
    except Exception as exc:
        logger.error(f"[MarketPainPipeline] Phase 1 FAILED: {exc}")
        return []

    if not raw_posts:
        logger.warning("[MarketPainPipeline] No posts ingested — aborting")
        return []

    # ── Phase 2a: Metadata Filtering ──
    try:
        metadata_filtered = filter_by_metadata(raw_posts)
    except Exception as exc:
        logger.error(f"[MarketPainPipeline] Metadata filter failed: {exc}")
        metadata_filtered = raw_posts  # degrade gracefully

    # ── Phase 2b: Tech Relevance Classification ──
    try:
        relevance_filtered = classify_relevance(metadata_filtered)
    except Exception as exc:
        logger.error(f"[MarketPainPipeline] Relevance classifier failed: {exc}")
        return []

    if not relevance_filtered:
        logger.warning("[MarketPainPipeline] No posts survived relevance filter")
        return []

    # ── Phase 3: Entity Extraction ──
    try:
        posts_with_entities = batch_extract_entities(relevance_filtered)
    except Exception as exc:
        logger.error(f"[MarketPainPipeline] Entity extraction failed: {exc}")
        return []

    # ── Phase 4: Business Validation ──
    try:
        validated = validate_business_relevance(posts_with_entities)
    except Exception as exc:
        logger.error(f"[MarketPainPipeline] Business validation failed: {exc}")
        validated = [(p, e, 0.5) for p, e in posts_with_entities]

    if not validated:
        logger.warning("[MarketPainPipeline] No posts survived business validation")
        return []

    # ── Phase 5+6: Frustration + Workflow Pain Detection ──
    signals: list[MarketPainSignalSchema] = []

    for post, entities, biz_relevance in validated:
        try:
            frustration = detect_frustration(post)
            workflow_pain = detect_workflow_pain(post)
        except Exception as exc:
            logger.warning(f"[MarketPainPipeline] Pain detection failed for {post.post_id}: {exc}")
            continue

        # Only keep signals with SOME pain detected (bypass for HN to ensure visibility)
        if post.subreddit != "hackernews" and not frustration.frustration_detected and not workflow_pain.workflow_pain_detected:
            continue

        # ── Phase 7: Capability Mapping ──
        try:
            capability = map_capability(
                workflow_pain.pain_category,
                entities.technologies,
            )
        except Exception:
            from app.services.market_pain.schemas import CapabilityMatch
            capability = CapabilityMatch()

        # Assemble the signal
        signal = MarketPainSignalSchema(
            post_id=post.post_id,
            source="f5bot" if post.subreddit == "hackernews" else "reddit",
            subreddit=post.subreddit,
            title=post.title,
            body=truncate_text(post.body, 1000),
            url=post.permalink or post.url,
            author=post.author,
            upvotes=post.upvotes,
            num_comments=post.num_comments,
            product=entities.products[0] if entities.products else None,
            company=entities.companies[0] if entities.companies else None,
            technologies=entities.technologies[:10],
            workflows=entities.workflows[:5],
            pain_category=workflow_pain.pain_category,
            pain_subcategories=workflow_pain.pain_subcategories[:5],
            workflow_pains=workflow_pain.pain_keywords_matched[:10],
            severity=workflow_pain.severity if workflow_pain.workflow_pain_detected else "low",
            tech_confidence=post.tech_relevance_score,
            sentiment_score=frustration.sentiment_score,
            business_relevance=biz_relevance,
            momentum_score=0.0,  # Computed in Phase 8
            capability_matches=capability.matched_practices,
            strategic_fit_score=capability.strategic_fit_score,
            matched_practices=capability.matched_practices,
            matched_accelerators=capability.matched_accelerators,
            timestamp=timestamp_from_utc(post.created_utc),
            created_utc=post.created_utc,
        )
        signals.append(signal)

    logger.info(
        f"[MarketPainPipeline] Pain detection: {len(validated)} validated → "
        f"{len(signals)} pain signals detected"
    )

    if not signals:
        return []

    # ── Phase 8: Temporal Momentum ──
    try:
        signals = compute_momentum_scores(signals)
    except Exception as exc:
        logger.warning(f"[MarketPainPipeline] Temporal analysis failed: {exc}")

    # ── Phase 9: Composite Scoring ──
    try:
        signals = score_all_signals(signals)
    except Exception as exc:
        logger.error(f"[MarketPainPipeline] Scoring failed: {exc}")

    # ── Phase 10: Top-N Selection ──
    top_signals = signals[:max_output]

    elapsed = round(time.time() - start, 2)
    sources_summary = ", ".join(f"{s.source}({s.subreddit})" for s in top_signals)
    logger.info(
        f"[MarketPainPipeline] COMPLETE in {elapsed}s: "
        f"{len(raw_posts)} ingested → {len(metadata_filtered)} filtered → "
        f"{len(relevance_filtered)} relevant → {len(validated)} validated → "
        f"{len(signals)} scored → {len(top_signals)} returned. Sources: {sources_summary}"
    )

    return top_signals
