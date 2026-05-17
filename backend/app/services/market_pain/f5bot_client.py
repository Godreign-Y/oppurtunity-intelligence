"""
app/services/market_pain/f5bot_client.py

F5Bot integration client — stub for future implementation.
F5Bot monitors Reddit/HackerNews for keyword mentions and sends email alerts.
This module will parse F5Bot webhook payloads or email digests when integrated.

Currently returns empty results. Designed for future extension.
"""

import httpx
import logging
from typing import Optional

from app.services.market_pain.schemas import RedditPost

logger = logging.getLogger(__name__)


async def fetch_f5bot_alerts(
    keywords: Optional[list[str]] = None,
) -> list[RedditPost]:
    """
    Fetch F5Bot keyword alert matches.
    Currently implemented via HackerNews Algolia API to provide active signals
    for the keywords/company name.
    """
    if not keywords:
        return []
        
    query = keywords[0]
    url = f"https://hn.algolia.com/api/v1/search?query={query}"
    
    posts: list[RedditPost] = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            hits = data.get("hits", [])
            
            for hit in hits:
                title = hit.get("title", "") or hit.get("story_title", "")
                body = hit.get("story_text", "") or hit.get("comment_text", "") or ""
                
                # Only keep if query is explicitly in title or body
                if query.lower() not in title.lower() and query.lower() not in body.lower():
                    continue
                    
                posts.append(
                    RedditPost(
                        post_id=str(hit.get("objectID", "")),
                        subreddit="hackernews",
                        title=title,
                        body=body,
                        author=hit.get("author", ""),
                        upvotes=hit.get("points", 0),
                        num_comments=hit.get("num_comments", 0),
                        url=hit.get("url", ""),
                        created_utc=float(hit.get("created_at_i", 0)),
                        permalink=f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    )
                )
        except Exception as exc:
            logger.error(f"[F5BotClient] HN fetch failed: {exc}")
            
    logger.info(f"[F5BotClient] Found {len(posts)} HackerNews signals for {query}")
    return posts
