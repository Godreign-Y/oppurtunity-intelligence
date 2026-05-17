"""
app/services/blog/blog_discovery.py

Discovers engineering blog URLs and RSS feeds for a company
via web search and common URL pattern probing.
"""

import httpx
import logging
from typing import Optional

from app.utils.search import discover_urls, search_tavily

logger = logging.getLogger(__name__)

BLOG_SEARCH_PATTERNS: list[str] = [
    "{company} engineering blog",
    "{company} tech blog",
    "{company} medium engineering",
    "{company} developer blog",
]

BLOG_URL_PATTERNS: list[str] = [
    "{domain}/engineering",
    "{domain}/blog",
    "{domain}/tech",
    "engineering.{domain}",
    "medium.com/{company}-engineering",
]

RSS_SUFFIXES: list[str] = ["/feed", "/rss", "/rss.xml", "/feed.xml"]


async def probe_rss_feed(base_url: str) -> Optional[str]:
    """
    Probe common RSS suffixes for a given base URL.

    Args:
        base_url: Base URL to try RSS suffixes on.

    Returns:
        Working RSS URL string, or None if none found.
    """
    async with httpx.AsyncClient(timeout=8.0) as client:
        for suffix in RSS_SUFFIXES:
            url = base_url.rstrip("/") + suffix
            try:
                response = await client.get(url, follow_redirects=True)
                content_type = response.headers.get("content-type", "")
                if response.status_code == 200 and (
                    "xml" in content_type or "rss" in content_type
                ):
                    logger.info(f"RSS feed found: {url}")
                    return url
            except httpx.HTTPError:
                continue
    return None


async def discover_blog_urls(company_name: str) -> list[str]:
    """
    Discover engineering blog URLs for a company.

    Combines web search results with RSS probing.

    Args:
        company_name: Company name to search for.

    Returns:
        List of discovered blog/RSS URLs.
    """
    logger.info(f"[BlogDiscovery] Discovering blogs for: {company_name}")
    urls = await discover_urls(company_name, BLOG_SEARCH_PATTERNS)

    company_slug = company_name.lower().replace(" ", "")
    company_parts = company_name.lower().split()

    # Filter to keep only likely engineering blog URLs THAT ALSO BELONG TO THE COMPANY
    blog_indicators = ["blog", "engineering", "tech", "medium.com", "dev.to", "rss"]
    filtered = []
    for url in urls:
        lower_url = url.lower()
        has_indicator = any(ind in lower_url for ind in blog_indicators)
        has_company = company_slug in lower_url or any(part in lower_url for part in company_parts if len(part) > 2)
        if has_indicator and has_company:
            filtered.append(url)

    logger.info(f"[BlogDiscovery] Found {len(filtered)} candidate blog URLs")
    return filtered[:8]  # Cap to avoid excessive downstream fetches
