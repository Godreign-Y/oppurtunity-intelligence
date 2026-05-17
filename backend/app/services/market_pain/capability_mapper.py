"""
app/services/market_pain/capability_mapper.py

Phase 7 — CRITICAL module.
Maps detected market pain to internal organizational capabilities.
Connects community frustrations to Relanto's service practices.

Capability registry is sourced from app/config/keywords/capability_registry.py — edit there.
"""

import logging

from app.services.market_pain.schemas import CapabilityMatch
from app.config.keywords.capability_registry import CAPABILITY_REGISTRY

logger = logging.getLogger(__name__)



def map_capability(
    pain_category: str,
    technologies: list[str],
) -> CapabilityMatch:
    """
    Map a detected pain category + technologies to internal organizational capabilities.

    Scoring:
    1. Base fit from pain category mapping (0.0–0.5)
    2. Technology overlap bonus (0.0–0.3)
    3. Multi-practice coverage bonus (0.0–0.2)

    Args:
        pain_category: Detected workflow pain category string.
        technologies: Technologies mentioned in the signal.

    Returns:
        CapabilityMatch with practices, accelerators, and strategic fit score.
    """
    registry = CAPABILITY_REGISTRY.get(pain_category)

    if not registry:
        return CapabilityMatch(
            capability_match=False,
            matched_practices=[],
            matched_accelerators=[],
            strategic_fit_score=0.0,
        )

    practices = registry["practices"]
    accelerators = registry["accelerators"]
    base_weight = registry["fit_weight"]
    registry_techs = registry["technologies"]

    # Base category fit (0.0–0.5)
    score = base_weight * 0.5

    # Technology overlap bonus (0.0–0.3)
    if registry_techs and technologies:
        tech_overlap = len(set(t.lower() for t in technologies) & set(registry_techs))
        tech_bonus = min(tech_overlap * 0.1, 0.3)
        score += tech_bonus

    # Multi-practice coverage bonus (0.0–0.2)
    if len(practices) >= 3:
        score += 0.2
    elif len(practices) >= 2:
        score += 0.12

    score = round(min(score, 1.0), 3)

    return CapabilityMatch(
        capability_match=score >= 0.3,
        matched_practices=practices,
        matched_accelerators=accelerators,
        strategic_fit_score=score,
    )
