"""
app/services/career/ats_extractor.py

Extracts job listings from supported ATS platforms:
  - Greenhouse (public JSON API)
  - Lever (public JSON API)
  - Ashby (HTML via Firecrawl)
  - Workday (HTML via Firecrawl — limited support)
"""

import httpx
import logging
import re
from typing import Optional

from app.utils.firecrawl import extract_markdown

logger = logging.getLogger(__name__)


async def extract_greenhouse_jobs(company_slug: str) -> list[dict]:
    """
    Fetch job postings from the Greenhouse public JSON API.

    Args:
        company_slug: Greenhouse board slug (e.g., 'vercel', 'stripe').

    Returns:
        List of raw job dicts from the Greenhouse API.
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("jobs", [])
        except httpx.HTTPError as exc:
            logger.error(f"Greenhouse fetch failed for slug '{company_slug}': {exc}")
            return []


async def extract_lever_jobs(company_slug: str) -> list[dict]:
    """
    Fetch job postings from the Lever public JSON API.

    Args:
        company_slug: Lever posting identifier (e.g., 'postman', 'vercel').

    Returns:
        List of raw job dicts from the Lever API.
    """
    url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"Lever fetch failed for slug '{company_slug}': {exc}")
            return []


async def extract_ashby_jobs(company_slug: str) -> list[dict]:
    """
    Extract job listings from Ashby job pages via Firecrawl.

    Args:
        company_slug: Ashby company slug.

    Returns:
        List of simplified job dicts extracted from markdown.
    """
    url = f"https://jobs.ashbyhq.com/{company_slug}"
    markdown = await extract_markdown(url)
    if not markdown:
        return []

    # Parse job titles from markdown — each job is typically a heading or line
    jobs: list[dict] = []
    lines = markdown.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or (len(stripped) > 5 and stripped[0].isupper()):
            title = stripped.lstrip("#").strip()
            if 3 < len(title) < 120:
                jobs.append({"title": title, "source": "ashby", "url": url})

    return jobs


async def extract_workday_jobs(company_domain: str) -> list[dict]:
    """
    Extract job listings from Workday job pages via Firecrawl (limited support).

    Args:
        company_domain: Workday subdomain pattern (e.g., 'company.wd1.myworkdayjobs.com').

    Returns:
        List of simplified job dicts extracted from page text.
    """
    url = f"https://{company_domain}"
    markdown = await extract_markdown(url)
    if not markdown:
        return []

    jobs: list[dict] = []
    lines = markdown.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("##") or (len(stripped) > 5 and stripped[0].isupper()):
            title = stripped.lstrip("#").strip()
            if 3 < len(title) < 120:
                jobs.append({"title": title, "source": "workday", "url": url})

    return jobs[:50]  # Cap to avoid noise from poorly structured Workday pages


def infer_slug_from_url(url: str, platform: str) -> Optional[str]:
    """
    Infer the ATS company slug from a discovered URL.

    Args:
        url: The discovered ATS URL.
        platform: ATS platform name ('greenhouse', 'lever', 'ashby', 'workday').

    Returns:
        Extracted slug string, or None if unable to parse.
    """
    patterns: dict[str, str] = {
        "greenhouse": r"boards(?:-api)?\.greenhouse\.io/(?:v1/boards/)?([^/?#]+)",
        "lever": r"(?:jobs\.lever\.co|api\.lever\.co/v0/postings)/([^/?#]+)",
        "ashby": r"jobs\.ashbyhq\.com/([^/?#]+)",
        "workday": r"([\w-]+\.wd\d+\.myworkdayjobs\.com)",
    }
    pattern = patterns.get(platform)
    if not pattern:
        return None
    match = re.search(pattern, url)
    return match.group(1) if match else None
