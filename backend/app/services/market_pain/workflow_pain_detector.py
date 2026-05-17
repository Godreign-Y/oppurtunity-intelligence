"""
app/services/market_pain/workflow_pain_detector.py

Phase 5b — THE MOST IMPORTANT MODULE.
Detects enterprise workflow pain, operational blockers, scaling failures,
and production reliability gaps. Goes far deeper than generic negativity.

Keyword taxonomy is sourced from app/config/keywords/workflow_pain_taxonomy.py — edit there.
"""

import logging

from app.services.market_pain.schemas import FilteredPost, WorkflowPainResult
from app.config.keywords.workflow_pain_taxonomy import (
    WORKFLOW_PAIN_TAXONOMY,
    SEVERITY_AMPLIFIERS,
)

logger = logging.getLogger(__name__)




def detect_workflow_pain(post: FilteredPost) -> WorkflowPainResult:
    """
    Detect enterprise workflow pain, operational blockers, and production issues.

    Scoring logic:
    1. Match against WORKFLOW_PAIN_TAXONOMY categories
    2. Pick the highest-weight matched category as primary
    3. Compute severity based on keyword density + amplifiers
    4. Return structured pain assessment

    Args:
        post: Relevance-filtered post.

    Returns:
        WorkflowPainResult with category, severity, and matched keywords.
    """
    combined = f"{post.title} {post.body}".lower()

    category_scores: dict[str, tuple[int, float, list[str]]] = {}

    for category, config in WORKFLOW_PAIN_TAXONOMY.items():
        keywords = config["keywords"]
        weight = config["weight"]
        matched = [kw for kw in keywords if kw in combined]

        if matched:
            category_scores[category] = (len(matched), weight, matched)

    if not category_scores:
        return WorkflowPainResult(
            workflow_pain_detected=False,
            pain_category="",
            pain_subcategories=[],
            severity="low",
            pain_keywords_matched=[],
        )

    # Primary category = highest (match_count * weight)
    primary = max(
        category_scores.items(),
        key=lambda x: x[1][0] * x[1][1],
    )
    primary_category = primary[0]
    primary_matches = primary[1][2]

    # Collect all matched subcategories
    subcategories = [cat for cat in category_scores if cat != primary_category]

    # All matched keywords across categories
    all_keywords: list[str] = []
    for _, (_, _, matched) in category_scores.items():
        all_keywords.extend(matched)

    # Compute severity
    amplifier_count = sum(1 for amp in SEVERITY_AMPLIFIERS if amp in combined)
    total_pain_matches = sum(count for count, _, _ in category_scores.values())

    if amplifier_count >= 3 or total_pain_matches >= 6:
        severity = "critical"
    elif amplifier_count >= 2 or total_pain_matches >= 4:
        severity = "high"
    elif amplifier_count >= 1 or total_pain_matches >= 2:
        severity = "medium"
    else:
        severity = "low"

    return WorkflowPainResult(
        workflow_pain_detected=True,
        pain_category=primary_category,
        pain_subcategories=subcategories,
        severity=severity,
        pain_keywords_matched=list(set(all_keywords))[:15],
    )
