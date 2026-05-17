"""
app/services/market_pain/business_validation.py

Phase 4 — Business relevance validation.
Rejects hobby projects, meme discussions, and non-commercial content.
Prioritizes enterprise products, production usage, and scaling conversations.
"""

import logging

from app.services.market_pain.schemas import FilteredPost, ExtractedEntities
from app.services.market_pain.entity_extractor import KNOWN_PRODUCTS

logger = logging.getLogger(__name__)

# Enterprise relevance indicators
ENTERPRISE_INDICATORS: list[str] = [
    "production", "enterprise", "our company", "our team", "our org",
    "at work", "in prod", "b2b", "client", "customer", "contract",
    "compliance", "soc2", "gdpr", "hipaa", "pci", "iso 27001",
    "vendor", "procurement", "license", "subscription", "pricing",
    "sla", "slo", "uptime", "availability", "incident",
    "deploy", "rollout", "migration", "scale", "infrastructure",
    "stakeholder", "management", "team lead", "engineering manager",
    "cto", "vp engineering", "director", "budget",
]

# Non-commercial noise indicators
NOISE_INDICATORS: list[str] = [
    "lol", "lmao", "meme", "shitpost", "upvote if",
    "eli5", "shower thought", "just kidding", "homework",
    "school project", "learning exercise", "toy project",
    "personal project", "side project", "for fun",
]


def compute_business_relevance(
    post: FilteredPost,
    entities: ExtractedEntities,
) -> float:
    """
    Compute a business relevance score (0.0 – 1.0).

    Scoring factors:
    - Known product mentions (weighted heavily)
    - Enterprise indicator keyword presence
    - Engagement metrics (upvotes, comments)
    - Noise penalty

    Args:
        post: Filtered post.
        entities: Extracted entities.

    Returns:
        Business relevance score.
    """
    combined = f"{post.title} {post.body}".lower()
    score = 0.0

    # Factor 1: Known product/company mentions (0.0–0.3)
    if entities.products:
        score += min(len(entities.products) * 0.15, 0.3)

    # Factor 2: Enterprise indicators (0.0–0.35)
    enterprise_matches = sum(1 for ind in ENTERPRISE_INDICATORS if ind in combined)
    score += min(enterprise_matches * 0.07, 0.35)

    # Factor 3: Engagement signal (0.0–0.2)
    if post.upvotes >= 50:
        score += 0.2
    elif post.upvotes >= 20:
        score += 0.15
    elif post.upvotes >= 10:
        score += 0.1
    elif post.upvotes >= 5:
        score += 0.05

    # Factor 4: Technology depth (0.0–0.15)
    if len(entities.technologies) >= 3:
        score += 0.15
    elif len(entities.technologies) >= 1:
        score += 0.08

    # Noise penalty
    noise_count = sum(1 for n in NOISE_INDICATORS if n in combined)
    if noise_count >= 2:
        score *= 0.3  # Heavy penalty
    elif noise_count >= 1:
        score *= 0.7  # Moderate penalty

    return round(min(score, 1.0), 3)


def validate_business_relevance(
    posts_with_entities: list[tuple[FilteredPost, ExtractedEntities]],
    min_relevance: float = 0.25,
) -> list[tuple[FilteredPost, ExtractedEntities, float]]:
    """
    Validate business relevance and reject non-commercial noise.

    Args:
        posts_with_entities: List of (post, entities) tuples.
        min_relevance: Minimum business relevance score to keep.

    Returns:
        List of (post, entities, relevance_score) for validated posts.
    """
    validated: list[tuple[FilteredPost, ExtractedEntities, float]] = []

    for post, entities in posts_with_entities:
        relevance = compute_business_relevance(post, entities)
        if post.subreddit == "hackernews" or relevance >= min_relevance:
            validated.append((post, entities, relevance))

    rejected = len(posts_with_entities) - len(validated)
    logger.info(
        f"[BusinessValidation] {len(posts_with_entities)} → {len(validated)} posts "
        f"({rejected} rejected below {min_relevance} relevance threshold)"
    )
    return validated
