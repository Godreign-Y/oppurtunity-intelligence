"""
app/utils/search.py

Utility functions for web search via Tavily and Serper APIs.
Used for ATS discovery and engineering blog discovery.
"""

import httpx
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


async def search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """
    Perform a web search using the Tavily Search API.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return.

    Returns:
        List of result dicts with keys: title, url, content.
    """
    if not settings.tavily_api_key:
        logger.warning("TAVILY_API_KEY not set — skipping Tavily search.")
        return []

    payload = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(
                "https://api.tavily.com/search", json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except httpx.HTTPError as exc:
            logger.error(f"Tavily search failed for '{query}': {exc}")
            return []


async def search_serper(query: str, max_results: int = 5) -> list[dict]:
    """
    Perform a web search using the Serper (Google Search) API.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return.

    Returns:
        List of result dicts with keys: title, link, snippet.
    """
    if not settings.serper_api_key:
        logger.warning("SERPER_API_KEY not set — skipping Serper search.")
        return []

    headers = {
        "X-API-KEY": settings.serper_api_key,
        "Content-Type": "application/json",
    }
    payload = {"q": query, "num": max_results}

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(
                "https://google.serper.dev/search", json=payload, headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("organic", [])
        except httpx.HTTPError as exc:
            logger.error(f"Serper search failed for '{query}': {exc}")
            return []


async def discover_urls(company_name: str, patterns: list[str]) -> list[str]:
    """
    Discover candidate URLs for a company using multiple search patterns.

    Tries Tavily first, falls back to Serper if Tavily returns no results.

    Args:
        company_name: Company name to search for.
        patterns: List of search query templates with {company} placeholder.

    Returns:
        Deduplicated list of discovered URLs.
    """
    urls: list[str] = []

    for pattern in patterns:
        query = pattern.format(company=company_name)
        results = await search_tavily(query, max_results=3)

        if not results:
            results = await search_serper(query, max_results=3)

        for r in results:
            url = r.get("url") or r.get("link")
            if url and url not in urls:
                urls.append(url)

    return urls
