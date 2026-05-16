"""
app/services/career/ats_discovery.py

Discovers which ATS platform a company uses (Greenhouse, Lever, Ashby, Workday)
via targeted web search using Tavily and Serper.
"""

import logging
from typing import Optional

from app.utils.search import discover_urls

logger = logging.getLogger(__name__)

ATS_SEARCH_PATTERNS: list[str] = [
    "{company} career page",
    "site:boards.greenhouse.io {company}",
    "site:jobs.lever.co {company}",
    "site:jobs.ashbyhq.com {company}",
    "site:myworkdayjobs.com {company}",
    "{company} jobs greenhouse",
    "{company} jobs lever",
]

ATS_URL_SIGNATURES: dict[str, str] = {
    "boards.greenhouse.io": "greenhouse",
    "boards-api.greenhouse.io": "greenhouse",
    "jobs.lever.co": "lever",
    "api.lever.co": "lever",
    "jobs.ashbyhq.com": "ashby",
    "myworkdayjobs.com": "workday",
    "ashbyhq.com": "ashby",
    "lever.co": "lever",
    "greenhouse.io": "greenhouse",
}


def detect_ats_from_urls(urls: list[str], company_name: str) -> tuple[Optional[str], Optional[str]]:
    """
    Detect ATS platform from a list of discovered URLs, prioritizing those that
    match the company name.

    Args:
        urls: List of candidate URLs from search results.
        company_name: Name of the company.

    Returns:
        Tuple of (ats_platform, ats_url) or (None, None) if not detected.
    """
    company_slug = company_name.lower().replace(" ", "")
    
    # First pass: look for exact slug matches
    for url in urls:
        lower_url = url.lower()
        if company_slug in lower_url:
            for signature, platform in ATS_URL_SIGNATURES.items():
                if signature in lower_url:
                    return platform, url
                    
    # Second pass: fallback to any signature match if no slug match
    for url in urls:
        for signature, platform in ATS_URL_SIGNATURES.items():
            if signature in url:
                return platform, url
                
    return None, None


async def discover_ats(company_name: str) -> tuple[Optional[str], Optional[str]]:
    """
    Discover the ATS platform and jobs URL for a given company.

    Args:
        company_name: Name of the company (e.g., "Stripe").

    Returns:
        Tuple of (ats_platform_name, ats_jobs_url).
        Returns (None, None) if no ATS is detected.
    """
    logger.info(f"Discovering ATS for company: {company_name}")
    urls = await discover_urls(company_name, ATS_SEARCH_PATTERNS)
    platform, url = detect_ats_from_urls(urls, company_name)

    if platform:
        logger.info(f"Detected ATS: {platform} at {url}")
    else:
        logger.warning(f"No ATS detected for {company_name}")

    return platform, url
