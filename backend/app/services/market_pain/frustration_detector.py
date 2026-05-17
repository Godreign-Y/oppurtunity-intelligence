"""
app/services/market_pain/frustration_detector.py

Phase 5a — Frustration detection using keyword patterns and rule-based scoring.
Detects negativity, complaints, and product frustration — NOT generic sentiment.
Specifically tuned for technology product frustration vs. general negativity.
"""

import logging

from app.services.market_pain.schemas import FilteredPost, FrustrationResult

logger = logging.getLogger(__name__)

# Strong frustration indicators (high weight)
STRONG_FRUSTRATION: list[str] = [
    "broken", "unusable", "terrible", "awful", "unacceptable",
    "nightmare", "disaster", "catastrophe", "worst", "horrible",
    "complete failure", "deal breaker", "showstopper", "critical bug",
    "data loss", "lost data", "corrupted", "destroyed",
    "impossible to use", "can't use", "unable to", "doesn't work",
    "stopped working", "keeps crashing", "keeps failing",
    "wasted hours", "wasted days", "wasted weeks",
    "switching away", "switched to", "moving away", "ditched",
    "cancelled subscription", "refund", "money back",
]

# Moderate frustration indicators (medium weight)
MODERATE_FRUSTRATION: list[str] = [
    "frustrating", "annoying", "disappointing", "unreliable",
    "inconsistent", "buggy", "flaky", "janky", "clunky",
    "slow", "laggy", "unresponsive", "timeout", "error",
    "workaround", "hack", "kludge", "band-aid", "duct tape",
    "not working", "barely works", "half-baked", "undocumented",
    "confusing", "misleading", "unclear", "poor documentation",
    "breaking change", "regression", "downgrade", "deprecated",
    "rate limited", "quota exceeded", "overpriced", "expensive",
    "no support", "support is terrible", "ghosted",
]

# Negation patterns that flip sentiment
NEGATION_PREFIXES: list[str] = [
    "not ", "no ", "don't ", "doesn't ", "isn't ", "aren't ",
    "wasn't ", "weren't ", "won't ", "can't ", "cannot ",
    "never ", "none ", "nothing ", "nobody ", "neither ",
]


def detect_frustration(post: FilteredPost) -> FrustrationResult:
    """
    Detect product/technology frustration in a post.

    Scoring:
    - Strong frustration keywords: +0.15 each (capped)
    - Moderate frustration keywords: +0.08 each (capped)
    - Negation context bonus: +0.1
    - Multiple keyword overlap bonus: +0.1

    Args:
        post: Relevance-filtered post.

    Returns:
        FrustrationResult with detection flag, score, and matched keywords.
    """
    combined = f"{post.title} {post.body}".lower()

    strong_matches: list[str] = []
    moderate_matches: list[str] = []

    # Check strong frustration
    for kw in STRONG_FRUSTRATION:
        if kw in combined:
            strong_matches.append(kw)

    # Check moderate frustration
    for kw in MODERATE_FRUSTRATION:
        if kw in combined:
            moderate_matches.append(kw)

    if not strong_matches and not moderate_matches:
        return FrustrationResult(
            frustration_detected=False,
            sentiment_score=0.0,
            frustration_keywords=[],
        )

    # Compute frustration score
    score = 0.0
    score += min(len(strong_matches) * 0.15, 0.5)
    score += min(len(moderate_matches) * 0.08, 0.35)

    # Negation context bonus
    has_negation = any(neg in combined for neg in NEGATION_PREFIXES)
    if has_negation:
        score += 0.1

    # Multi-match bonus
    total_matches = len(strong_matches) + len(moderate_matches)
    if total_matches >= 4:
        score += 0.1

    score = round(min(score, 1.0), 3)
    all_keywords = strong_matches + moderate_matches

    return FrustrationResult(
        frustration_detected=score >= 0.25,
        sentiment_score=-score,  # Negative sentiment
        frustration_keywords=all_keywords[:10],
    )
