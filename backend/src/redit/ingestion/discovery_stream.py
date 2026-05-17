"""Merge feeds, subreddit streams, and search into a deduplicated post stream."""

import asyncio
from collections.abc import AsyncIterator

from redit.ingestion.base import RedditSource
from redit.models.discovery import GlobalFeed
from redit.models.reddit import RawRedditPost, RedditSort


async def iter_discovery_posts(
    source: RedditSource,
    feeds: list[GlobalFeed],
    subreddits: list[str],
    search_queries: list[str],
    sort: RedditSort,
    limit_per_source: int,
    delay_seconds: float = 0.0,
) -> AsyncIterator[RawRedditPost]:
    """
    Yield unique posts from:
    - global feeds
    - subreddit feeds
    - search queries

    Deduplicates by Reddit post id.
    """

    seen_ids: set[str] = set()

    search_sort: RedditSort = (
        sort if sort in ("hot", "new", "top", "relevance")
        else "relevance"
    )

    # ---------------------------------------------------
    # Global feeds
    # ---------------------------------------------------

    for feed in feeds:

        async for post in source.iter_global_feed(
            feed=feed,
            sort=sort,
            limit=limit_per_source,
        ):
            if post.id in seen_ids:
                continue

            seen_ids.add(post.id)

            yield post

        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

    # ---------------------------------------------------
    # Subreddit feeds
    # ---------------------------------------------------

    for subreddit in subreddits:

        async for post in source.iter_subreddit_feed(
            subreddit=subreddit,
            sort=sort,
            limit=limit_per_source,
        ):
            if post.id in seen_ids:
                continue

            seen_ids.add(post.id)

            yield post

        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

    # ---------------------------------------------------
    # Search queries
    # ---------------------------------------------------

    for query in search_queries:

        async for post in source.iter_search(
            query=query,
            sort=search_sort,
            limit=limit_per_source,
        ):
            if post.id in seen_ids:
                continue

            seen_ids.add(post.id)

            yield post

        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)