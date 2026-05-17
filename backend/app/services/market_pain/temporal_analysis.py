"""
app/services/market_pain/temporal_analysis.py

Phase 6 — Temporal intelligence.
Tracks repeated complaints, pain acceleration, sudden spikes.
Distinguishes: 5 complaints over 6 months ≠ 200 complaints in 2 weeks.
"""

import logging
import time
from collections import defaultdict

from app.services.market_pain.schemas import MarketPainSignalSchema

logger = logging.getLogger(__name__)


def compute_momentum_scores(
    signals: list[MarketPainSignalSchema],
) -> list[MarketPainSignalSchema]:
    """
    Compute temporal momentum scores for market pain signals.

    Momentum factors:
    1. Pain frequency per category — how many signals share this pain?
    2. Recency weighting — newer complaints score higher
    3. Engagement acceleration — high upvotes on recent posts = spike
    4. Cross-subreddit validation — same pain across subreddits = systemic

    Args:
        signals: List of assembled MarketPainSignalSchema objects (pre-scored).

    Returns:
        Same signals with updated momentum_score values.
    """
    if not signals:
        return signals

    now = time.time()

    # Group by pain category
    category_groups: dict[str, list[MarketPainSignalSchema]] = defaultdict(list)
    for sig in signals:
        if sig.pain_category:
            category_groups[sig.pain_category].append(sig)

    # Group by product
    product_groups: dict[str, list[MarketPainSignalSchema]] = defaultdict(list)
    for sig in signals:
        if sig.product:
            product_groups[sig.product].append(sig)

    for signal in signals:
        momentum = 0.0

        # Factor 1: Category frequency (0.0–0.3)
        cat_count = len(category_groups.get(signal.pain_category, []))
        momentum += min(cat_count * 0.06, 0.3)

        # Factor 2: Recency weighting (0.0–0.25)
        if signal.created_utc > 0:
            age_days = (now - signal.created_utc) / 86400
            if age_days <= 3:
                momentum += 0.25
            elif age_days <= 7:
                momentum += 0.2
            elif age_days <= 14:
                momentum += 0.15
            elif age_days <= 30:
                momentum += 0.08

        # Factor 3: Engagement acceleration (0.0–0.25)
        if signal.upvotes >= 100:
            momentum += 0.25
        elif signal.upvotes >= 50:
            momentum += 0.2
        elif signal.upvotes >= 25:
            momentum += 0.15
        elif signal.upvotes >= 10:
            momentum += 0.08

        # Factor 4: Cross-subreddit validation (0.0–0.2)
        if signal.product:
            product_subs = set(
                s.subreddit for s in product_groups.get(signal.product, [])
            )
            if len(product_subs) >= 3:
                momentum += 0.2
            elif len(product_subs) >= 2:
                momentum += 0.12

        signal.momentum_score = round(min(momentum, 1.0), 3)

    avg_momentum = sum(s.momentum_score for s in signals) / len(signals)
    logger.info(
        f"[TemporalAnalysis] Computed momentum for {len(signals)} signals "
        f"(avg: {avg_momentum:.3f})"
    )
    return signals
