"""
app/services/market_pain/metadata_filters.py

Phase 2, Step 1 — Cheap metadata filtering before any NLP processing.
Rejects noise early: short posts, low engagement, stale content, deleted posts.
"""

import logging
import time

from app.services.market_pain.schemas import RedditPost

logger = logging.getLogger(__name__)

# Configurable thresholds
MIN_TEXT_LENGTH: int = 50
MIN_UPVOTES: int = 3
MAX_AGE_DAYS: int = 30


def filter_by_metadata(
    posts: list[RedditPost],
    min_text_length: int = MIN_TEXT_LENGTH,
    min_upvotes: int = MIN_UPVOTES,
    max_age_days: int = MAX_AGE_DAYS,
) -> list[RedditPost]:
    """
    Apply cheap metadata filters to reject noise before expensive NLP.

    Filters applied in order of cheapness:
    1. Deleted/removed content check
    2. Minimum text length (title + body)
    3. Minimum upvote threshold
    4. Recency filter (max age in days)

    Args:
        posts: Raw RedditPost objects.
        min_text_length: Minimum combined title+body character count.
        min_upvotes: Minimum upvote count.
        max_age_days: Maximum post age in days.

    Returns:
        List of posts that survived all metadata filters.
    """
    now = time.time()
    max_age_seconds = max_age_days * 86400
    passed: list[RedditPost] = []

    for post in posts:
        # Filter 1: Deleted/removed content
        if post.body in ("[removed]", "[deleted]", ""):
            combined_text = post.title
        else:
            combined_text = f"{post.title} {post.body}"

        # Filter 2: Minimum text length
        if len(combined_text.strip()) < min_text_length:
            continue

        # Filter 3: Minimum upvotes (engagement signal)
        if post.subreddit != "hackernews" and post.upvotes < min_upvotes:
            continue

        # Filter 4: Recency — reject stale posts
        if post.subreddit != "hackernews" and post.created_utc > 0:
            age = now - post.created_utc
            if age > max_age_seconds:
                continue

        passed.append(post)

    rejected = len(posts) - len(passed)
    logger.info(
        f"[MetadataFilter] {len(posts)} → {len(passed)} posts "
        f"({rejected} rejected by metadata filters)"
    )
    return passed
