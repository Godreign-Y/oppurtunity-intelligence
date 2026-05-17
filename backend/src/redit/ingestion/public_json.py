"""Reddit ingestion via public .json endpoints (no OAuth)."""

from collections.abc import AsyncIterator
from typing import Any

import asyncio
import httpx

from redit.config.settings import Settings
from redit.ingestion.base import RedditSource
from redit.models.discovery import GlobalFeed
from redit.models.reddit import RawRedditPost, RedditSort
from redit.utils.logging import get_logger

logger = get_logger(__name__)

REDDIT_JSON_BASE = "https://www.reddit.com"

# Reddit hard caps each request to ~100 posts
MAX_BATCH_SIZE = 100


class PublicJsonRedditSource(RedditSource):
    """
    Fetches Reddit feeds and search results from public JSON endpoints.

    Supports pagination using Reddit's `after` cursor
    so large-scale ingestion (thousands of posts) works correctly.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize HTTP client with configured User-Agent."""
        self._settings = settings

        self._client = httpx.AsyncClient(
            base_url=REDDIT_JSON_BASE,
            headers={"User-Agent": settings.reddit_user_agent},
            timeout=settings.reddit_request_timeout_seconds,
            follow_redirects=True,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def iter_global_feed(
        self,
        feed: GlobalFeed,
        sort: RedditSort = "hot",
        limit: int = 25,
    ) -> AsyncIterator[RawRedditPost]:
        """
        Fetch paginated posts from global feeds like:
        - r/all
        - r/popular
        """

        path = f"/r/{feed}/{sort}.json"

        params = {
            "limit": limit,
            "raw_json": "1",
        }

        logger.info(
            "Fetching global feed",
            extra={
                "feed": feed,
                "sort": sort,
                "limit": limit,
            },
        )

        async for post in self._fetch_listing(path, params):
            yield post

    async def iter_subreddit_feed(
        self,
        subreddit: str,
        sort: RedditSort = "new",
        limit: int = 25,
    ) -> AsyncIterator[RawRedditPost]:
        """
        Fetch paginated posts from a specific subreddit.
        """

        path = f"/r/{subreddit}/{sort}.json"

        params = {
            "limit": limit,
            "raw_json": "1",
        }

        logger.info(
            "Fetching subreddit feed",
            extra={
                "subreddit": subreddit,
                "sort": sort,
                "limit": limit,
            },
        )

        async for post in self._fetch_listing(path, params):
            yield post

    async def iter_search(
        self,
        query: str,
        sort: RedditSort = "relevance",
        limit: int = 25,
    ) -> AsyncIterator[RawRedditPost]:
        """
        Fetch paginated Reddit search results.
        """

        params = {
            "q": query,
            "sort": sort,
            "limit": limit,
            "type": "link",
            "raw_json": "1",
        }

        logger.info(
            "Fetching Reddit search",
            extra={
                "query": query,
                "sort": sort,
                "limit": limit,
            },
        )

        async for post in self._fetch_listing("/search.json", params):
            yield post

    async def _fetch_listing(
        self,
        path: str,
        params: dict[str, Any],
    ) -> AsyncIterator[RawRedditPost]:
        """
        Fetch paginated Reddit listings using the `after` cursor.

        Reddit public JSON endpoints only return ~100 posts max per request.
        This method keeps requesting pages until:
        - requested limit reached
        - or no more pages remain
        """

        requested_limit = int(params.get("limit", 25))

        fetched = 0
        after = None

        while fetched < requested_limit:

            remaining = requested_limit - fetched

            batch_size = min(remaining, MAX_BATCH_SIZE)

            request_params = {
                **params,
                "limit": batch_size,
                "raw_json": "1",
            }

            if after:
                request_params["after"] = after

            logger.info(
                "Fetching Reddit page",
                extra={
                    "path": path,
                    "batch_size": batch_size,
                    "after": after,
                    "fetched_so_far": fetched,
                },
            )

            response = await self._client.get(path, params=request_params)

            response.raise_for_status()

            payload = response.json()

            data = payload.get("data", {})

            children = data.get("children", [])

            if not children:
                logger.info(
                    "No more Reddit results",
                    extra={"path": path},
                )
                break

            for child in children:

                post = self._parse_listing_child(child)

                if post is None:
                    continue

                yield post

                fetched += 1

                if fetched >= requested_limit:
                    break

            after = data.get("after")

            # No more pages available
            if not after:
                logger.info(
                    "Reached end of Reddit pagination",
                    extra={
                        "path": path,
                        "total_fetched": fetched,
                    },
                )
                break

            # Small delay to avoid hammering Reddit
            await asyncio.sleep(0.5)

    def _parse_listing_child(
        self,
        child: dict[str, Any],
    ) -> RawRedditPost | None:
        """Map Reddit listing child to RawRedditPost."""

        if child.get("kind") != "t3":
            return None

        data = child.get("data", {})

        post_id = data.get("name") or data.get("id")

        if not post_id:
            return None

        subreddit = (
            data.get("subreddit")
            or data.get("subreddit_name_prefixed", "").replace("r/", "")
        )

        if not subreddit:
            subreddit = "unknown"

        permalink = data.get("permalink", "")

        if permalink and not permalink.startswith("http"):
            permalink = f"{REDDIT_JSON_BASE}{permalink}"

        return RawRedditPost(
            id=str(post_id),
            subreddit=subreddit,
            title=data.get("title", "") or "",
            body=data.get("selftext", "") or "",
            score=int(data.get("score", 0) or 0),
            created_utc=float(data.get("created_utc", 0) or 0),
            permalink=permalink,
            url=data.get("url"),
            author=data.get("author"),
            num_comments=int(data.get("num_comments", 0) or 0),
        )