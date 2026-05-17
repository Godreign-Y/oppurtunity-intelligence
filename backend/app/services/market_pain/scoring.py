"""
app/services/market_pain/scoring.py

Phase 8 — Composite scoring engine.
NOT simple sentiment scoring. Combines 7 weighted factors into a
Unified Market Pain Opportunity Score.
"""

import logging

from app.services.market_pain.schemas import MarketPainSignalSchema

logger = logging.getLogger(__name__)

# Scoring weights — must sum to 1.0
SCORE_WEIGHTS: dict[str, float] = {
    "pain_severity": 0.25,
    "enterprise_relevance": 0.15,
    "momentum": 0.15,
    "capability_fit": 0.20,
    "business_relevance": 0.10,
    "engagement": 0.10,
    "tech_confidence": 0.05,
}

# Severity → numeric mapping
SEVERITY_SCORES: dict[str, float] = {
    "critical": 1.0,
    "high": 0.80,
    "medium": 0.55,
    "low": 0.30,
}


def compute_composite_score(signal: MarketPainSignalSchema) -> float:
    """
    Compute the final Unified Market Pain Opportunity Score.

    Factors:
    1. Pain severity (0.0–1.0) — how critical is the pain?
    2. Enterprise relevance (0.0–1.0) — is this enterprise-grade?
    3. Momentum (0.0–1.0) — is this accelerating?
    4. Capability fit (0.0–1.0) — can we address this?
    5. Business relevance (0.0–1.0) — is this commercially meaningful?
    6. Engagement (0.0–1.0) — how much community validation?
    7. Tech confidence (0.0–1.0) — how relevant is the tech?

    Args:
        signal: Fully enriched MarketPainSignalSchema.

    Returns:
        Composite confidence score (0.0–1.0).
    """
    # Factor 1: Pain severity
    severity_score = SEVERITY_SCORES.get(signal.severity, 0.3)

    # Factor 2: Enterprise relevance (derived from business_relevance)
    enterprise_score = signal.business_relevance

    # Factor 3: Momentum
    momentum_score = signal.momentum_score

    # Factor 4: Capability fit
    capability_score = signal.strategic_fit_score

    # Factor 5: Business relevance
    business_score = signal.business_relevance

    # Factor 6: Engagement signal
    if signal.upvotes >= 100:
        engagement_score = 1.0
    elif signal.upvotes >= 50:
        engagement_score = 0.8
    elif signal.upvotes >= 25:
        engagement_score = 0.6
    elif signal.upvotes >= 10:
        engagement_score = 0.4
    else:
        engagement_score = 0.2

    # Factor 7: Tech confidence
    tech_score = signal.tech_confidence

    # Weighted composite
    composite = (
        severity_score * SCORE_WEIGHTS["pain_severity"]
        + enterprise_score * SCORE_WEIGHTS["enterprise_relevance"]
        + momentum_score * SCORE_WEIGHTS["momentum"]
        + capability_score * SCORE_WEIGHTS["capability_fit"]
        + business_score * SCORE_WEIGHTS["business_relevance"]
        + engagement_score * SCORE_WEIGHTS["engagement"]
        + tech_score * SCORE_WEIGHTS["tech_confidence"]
    )

    if signal.source == "f5bot":
        composite += 0.40  # Boost HackerNews / F5Bot alerts to guarantee they show up in top 10!

    return round(min(composite, 1.0), 3)


def score_all_signals(
    signals: list[MarketPainSignalSchema],
) -> list[MarketPainSignalSchema]:
    """
    Apply composite scoring to all signals and sort by score.

    Args:
        signals: List of enriched MarketPainSignalSchema objects.

    Returns:
        Signals with updated confidence scores, sorted descending.
    """
    for signal in signals:
        signal.confidence = compute_composite_score(signal)

    # Sort by composite score descending
    signals.sort(key=lambda s: s.confidence, reverse=True)

    if signals:
        top = signals[0].confidence
        bottom = signals[-1].confidence
        logger.info(
            f"[ScoringEngine] Scored {len(signals)} signals "
            f"(top: {top:.3f}, bottom: {bottom:.3f})"
        )

    return signals
