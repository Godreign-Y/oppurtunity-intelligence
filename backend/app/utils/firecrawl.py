"""
app/utils/firecrawl.py

Utility for extracting clean markdown from web pages using the Firecrawl API.
Reduces LLM noise by stripping ads, scripts, and irrelevant HTML.
"""

import httpx
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

FIRECRAWL_SCRAPE_URL = "https://api.firecrawl.dev/v1/scrape"


async def extract_markdown(url: str) -> Optional[str]:
    """
    Extract clean markdown content from a URL using Firecrawl.

    Args:
        url: The target URL to scrape.

    Returns:
        Clean markdown string, or None if extraction fails.
    """
    if not settings.firecrawl_api_key:
        logger.warning("FIRECRAWL_API_KEY not set — falling back to raw fetch.")
        return await _raw_fetch_text(url)

    headers = {
        "Authorization": f"Bearer {settings.firecrawl_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "url": url,
        "formats": ["markdown"],
        "onlyMainContent": True,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                FIRECRAWL_SCRAPE_URL, json=payload, headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("markdown", None)
        except httpx.HTTPError as exc:
            logger.error(f"Firecrawl extraction failed for '{url}': {exc}")
            return None


async def _raw_fetch_text(url: str) -> Optional[str]:
    """
    Fallback: fetch raw HTML text from a URL without Firecrawl.

    Args:
        url: Target URL.

    Returns:
        Raw response text, or None on failure.
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as exc:
            logger.error(f"Raw fetch failed for '{url}': {exc}")
            return None
