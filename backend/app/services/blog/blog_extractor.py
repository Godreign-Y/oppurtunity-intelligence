"""
app/services/blog/blog_extractor.py

Extracts clean article content from engineering blogs using Firecrawl
and RSS feed parsing via feedparser.
"""

import feedparser
import httpx
import logging
from typing import Optional

from app.utils.firecrawl import extract_markdown

logger = logging.getLogger(__name__)


async def fetch_rss_articles(rss_url: str, max_articles: int = 5) -> list[dict]:
    """
    Fetch recent articles from an RSS feed.

    Args:
        rss_url: URL of the RSS/Atom feed.
        max_articles: Maximum number of articles to return.

    Returns:
        List of article dicts with keys: title, link, summary.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(rss_url, follow_redirects=True)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
            articles: list[dict] = []
            for entry in feed.entries[:max_articles]:
                articles.append(
                    {
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "summary": entry.get("summary", "")[:1000],
                    }
                )
            return articles
        except Exception as exc:
            logger.error(f"RSS fetch failed for '{rss_url}': {exc}")
            return []


async def fetch_blog_page_articles(blog_url: str, max_articles: int = 5) -> list[dict]:
    """
    Fetch article links and content from a blog landing page via Firecrawl.

    Args:
        blog_url: URL of the engineering blog landing page.
        max_articles: Maximum number of articles to extract.

    Returns:
        List of article dicts with keys: title, content, url.
    """
    markdown = await extract_markdown(blog_url)
    if not markdown:
        return []

    # Extract article entries from markdown — look for heading + link patterns
    articles: list[dict] = []
    lines = markdown.split("\n")
    current_title = ""
    buffer: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("##"):
            if current_title and buffer:
                articles.append(
                    {
                        "title": current_title,
                        "content": " ".join(buffer[:20]),
                        "url": blog_url,
                    }
                )
                if len(articles) >= max_articles:
                    break
                buffer = []
            current_title = stripped.lstrip("#").strip()
        elif stripped and current_title:
            buffer.append(stripped)

    return articles


async def extract_article_content(article_url: str) -> Optional[str]:
    """
    Extract full clean content from a single blog article URL.

    Args:
        article_url: URL of the article.

    Returns:
        Clean markdown string of the article, or None.
    """
    logger.info(f"[BlogExtractor] Extracting article: {article_url}")
    return await extract_markdown(article_url)
