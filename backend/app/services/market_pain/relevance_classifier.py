"""
app/services/market_pain/relevance_classifier.py

Phase 2, Steps 2 & 3 — Tech relevance filtering + lightweight semantic classification.
Two-layer approach: cheap keyword pre-filter, then semantic confidence scoring.
Does NOT use expensive LLMs — uses keyword matching and rule-based heuristics.

Keywords are sourced from app/config/keywords/reddit_relevance_keywords.py — edit there.
"""

import logging
import re
from typing import Optional

from app.services.market_pain.schemas import RedditPost, FilteredPost
from app.config.keywords.reddit_relevance_keywords import (
    REDDIT_TECH_KEYWORDS,
    REDDIT_DOMAIN_CLASSIFIERS,
    REDDIT_MIN_TECH_KEYWORD_MATCHES,
    REDDIT_MIN_SEMANTIC_CONFIDENCE,
)

logger = logging.getLogger(__name__)

# Aliases for backward compat with existing code in this file
TECH_KEYWORDS = REDDIT_TECH_KEYWORDS
DOMAIN_CLASSIFIERS = REDDIT_DOMAIN_CLASSIFIERS
MIN_TECH_KEYWORD_MATCHES = REDDIT_MIN_TECH_KEYWORD_MATCHES
MIN_SEMANTIC_CONFIDENCE = REDDIT_MIN_SEMANTIC_CONFIDENCE


def _count_keyword_matches(text: str, keywords: list[str]) -> int:
    """Count how many keywords appear in the text."""
    lower = text.lower()
    return sum(1 for kw in keywords if kw in lower)


def _compute_semantic_score(text: str) -> tuple[float, str]:
    """
    Compute a semantic relevance score using rule-based domain classification.
    Returns (confidence, best_label).
    """
    lower = text.lower()
    best_score = 0.0
    best_label = "general"

    for label, patterns in DOMAIN_CLASSIFIERS.items():
        matches = sum(1 for p in patterns if p in lower)
        # Normalize by pattern count, with diminishing returns
        score = min(matches / 4.0, 1.0)

        if score > best_score:
            best_score = score
            best_label = label

    return best_score, best_label


def classify_relevance(
    posts: list[RedditPost],
    min_confidence: float = MIN_SEMANTIC_CONFIDENCE,
) -> list[FilteredPost]:
    """
    Two-layer relevance classification:
    1. Cheap keyword pre-filter — reject if zero tech keyword matches
    2. Semantic domain scoring — reject if confidence below threshold

    Args:
        posts: Metadata-filtered RedditPost objects.
        min_confidence: Minimum semantic confidence to keep.

    Returns:
        List of FilteredPost objects with relevance scores attached.
    """
    passed: list[FilteredPost] = []

    for post in posts:
        combined = f"{post.title} {post.body}"

        # Layer 1: Keyword pre-filter
        tech_matches = _count_keyword_matches(combined, TECH_KEYWORDS)
        if post.subreddit != "hackernews" and tech_matches < MIN_TECH_KEYWORD_MATCHES:
            continue

        # Layer 2: Semantic domain classification
        sem_score, sem_label = _compute_semantic_score(combined)
        if post.subreddit != "hackernews" and sem_score < min_confidence:
            continue

        # Compute blended relevance score
        keyword_score = min(tech_matches / 5.0, 1.0)
        blended = (keyword_score * 0.4) + (sem_score * 0.6)

        passed.append(
            FilteredPost(
                post_id=post.post_id,
                subreddit=post.subreddit,
                title=post.title,
                body=post.body,
                author=post.author,
                upvotes=post.upvotes,
                num_comments=post.num_comments,
                url=post.url,
                permalink=post.permalink,
                created_utc=post.created_utc,
                tech_relevance_score=round(blended, 3),
                relevance_label=sem_label,
            )
        )

    rejected = len(posts) - len(passed)
    logger.info(
        f"[RelevanceClassifier] {len(posts)} → {len(passed)} posts "
        f"({rejected} rejected by relevance filter)"
    )
    return passed
