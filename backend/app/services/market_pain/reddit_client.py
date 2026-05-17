"""
app/services/market_pain/reddit_client.py

Async Reddit data ingestion using the public JSON API.
No OAuth or PRAW dependency — uses httpx to hit Reddit's public .json endpoints.
Aggressively limited: 50-100 posts per subreddit max.
"""

import httpx
import logging
import time
from typing import Optional

from app.services.market_pain.schemas import RedditPost

logger = logging.getLogger(__name__)

REDDIT_BASE = "https://www.reddit.com"
USER_AGENT = "OpportunityIntel/1.0 (Market Pain Intelligence Pipeline)"

# Rate limiting — Reddit public API allows ~60 req/min
_last_request_time: float = 0.0
_MIN_REQUEST_INTERVAL: float = 1.1  # seconds between requests


async def _rate_limited_get(client: httpx.AsyncClient, url: str) -> Optional[dict]:
    """Make a rate-limited GET request to Reddit's public JSON API."""
    global _last_request_time

    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < _MIN_REQUEST_INTERVAL:
        import asyncio
        await asyncio.sleep(_MIN_REQUEST_INTERVAL - elapsed)

    _last_request_time = time.time()

    try:
        response = await client.get(
            url,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        logger.warning(f"[RedditClient] HTTP error fetching {url}: {exc}")
        return None
    except Exception as exc:
        logger.warning(f"[RedditClient] Unexpected error fetching {url}: {exc}")
        return None


def _parse_posts(data: Optional[dict], subreddit: str) -> list[RedditPost]:
    """Parse Reddit JSON listing response into RedditPost objects."""
    if not data:
        return []

    posts: list[RedditPost] = []
    children = data.get("data", {}).get("children", [])

    for child in children:
        kind = child.get("kind", "")
        if kind != "t3":  # t3 = link/post
            continue

        d = child.get("data", {})

        # Skip stickied, removed, or deleted posts
        if d.get("stickied", False):
            continue
        if d.get("removed_by_category"):
            continue
        if d.get("selftext") in ("[removed]", "[deleted]"):
            continue

        title = d.get("title", "").strip()
        body = d.get("selftext", "").strip()

        posts.append(
            RedditPost(
                post_id=d.get("id", ""),
                subreddit=d.get("subreddit", subreddit),
                title=title,
                body=body,
                author=d.get("author", ""),
                upvotes=d.get("ups", 0),
                num_comments=d.get("num_comments", 0),
                url=d.get("url", ""),
                created_utc=d.get("created_utc", 0.0),
                permalink=f"https://reddit.com{d.get('permalink', '')}",
            )
        )

    return posts


async def fetch_subreddit_posts(
    subreddit: str,
    sort: str = "hot",
    limit: int = 50,
    query: Optional[str] = None,
) -> list[RedditPost]:
    """
    Fetch recent posts from a single subreddit.

    Args:
        subreddit: Subreddit name (without r/).
        sort: Sort order — 'hot', 'top', 'new'.
        limit: Max posts to fetch (capped at 100).
        query: Optional search query (e.g., company name).

    Returns:
        List of RedditPost objects.
    """
    limit = min(limit, 100)
    
    if query:
        url = f"{REDDIT_BASE}/r/{subreddit}/search.json?q={query}&restrict_sr=1&sort={sort}&limit={limit}"
    else:
        url = f"{REDDIT_BASE}/r/{subreddit}/{sort}.json?limit={limit}&t=month"

    async with httpx.AsyncClient(timeout=15.0) as client:
        data = await _rate_limited_get(client, url)

    posts = _parse_posts(data, subreddit)
    logger.info(f"[RedditClient] Fetched {len(posts)} posts from r/{subreddit} ({sort})")
    return posts


async def fetch_all_subreddits(
    subreddits: list[str],
    limit_per_sub: int = 50,
    query: Optional[str] = None,
) -> list[RedditPost]:
    """
    Fetch posts from multiple subreddits sequentially (respecting rate limits).

    Args:
        subreddits: List of subreddit names.
        limit_per_sub: Posts per subreddit.
        query: Optional search query.

    Returns:
        Combined list of RedditPost objects.
    """
    all_posts: list[RedditPost] = []

    # For query-based searches, we can combine all subreddits into a multi-reddit
    # to dramatically reduce the number of API requests and time taken.
    if query and subreddits:
        multi_sub = "+".join(subreddits)
        try:
            posts = await fetch_subreddit_posts(multi_sub, sort="new", limit=100, query=query)
            all_posts.extend(posts)
        except Exception as exc:
            logger.warning(f"[RedditClient] Failed to fetch multi-reddit: {exc}")
    else:
        for sub in subreddits:
            try:
                posts = await fetch_subreddit_posts(sub, sort="hot", limit=limit_per_sub, query=query)
                all_posts.extend(posts)
            except Exception as exc:
                logger.warning(f"[RedditClient] Failed to fetch r/{sub}: {exc}")
                continue

    logger.info(f"[RedditClient] Total fetched: {len(all_posts)} posts from {len(subreddits)} subreddits")
    return all_posts
