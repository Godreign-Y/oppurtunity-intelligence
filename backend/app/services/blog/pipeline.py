"""
app/services/blog/pipeline.py

Orchestrates the full engineering blog intelligence pipeline:
  1. Discover blog URLs
  2. Extract article content
  3. Generate normalized signals
"""

import logging
from typing import Optional

from app.services.blog.blog_discovery import discover_blog_urls, probe_rss_feed
from app.services.blog.blog_extractor import (
    fetch_rss_articles,
    fetch_blog_page_articles,
    extract_article_content,
)
from app.services.blog.signal_extractor import extract_signal_from_article
from app.schemas.signal import UnifiedSignalSchema

logger = logging.getLogger(__name__)

MAX_ARTICLES_PER_BLOG = 5


async def run_blog_pipeline(
    company_name: str,
) -> tuple[list[UnifiedSignalSchema], Optional[str]]:
    """
    Run the full engineering blog intelligence pipeline for a company.

    Steps:
      1. Discover candidate blog URLs via web search.
      2. Probe for RSS feeds; fall back to HTML extraction if none found.
      3. Extract article content from discovered posts.
      4. Extract normalized signals from each article.

    Args:
        company_name: Name of the company to analyze.

    Returns:
        Tuple of:
          - list of UnifiedSignalSchema instances
          - discovered blog URL (or None)
    """
    logger.info(f"[BlogPipeline] Starting for: {company_name}")

    blog_urls = await discover_blog_urls(company_name)
    if not blog_urls:
        logger.warning(f"[BlogPipeline] No blog URLs found for {company_name}")
        return [], None

    primary_blog_url = blog_urls[0]
    signals: list[UnifiedSignalSchema] = []

    for blog_url in blog_urls[:3]:
        rss_url = await probe_rss_feed(blog_url)

        if rss_url:
            articles = await fetch_rss_articles(rss_url, max_articles=MAX_ARTICLES_PER_BLOG)
        else:
            articles = await fetch_blog_page_articles(
                blog_url, max_articles=MAX_ARTICLES_PER_BLOG
            )

        for article in articles:
            article_url = article.get("link") or article.get("url", blog_url)
            title = article.get("title", "")
            # Prefer pre-fetched summary; fall back to full article fetch
            content = article.get("summary") or article.get("content") or ""

            if len(content) < 200 and article_url != blog_url:
                content = await extract_article_content(article_url) or content

            signal = extract_signal_from_article(title, content, article_url, company_name)
            if signal:
                signals.append(signal)

    logger.info(
        f"[BlogPipeline] {len(signals)} signals extracted for {company_name}"
    )
    return signals, primary_blog_url
