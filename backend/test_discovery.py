import asyncio
import logging
from app.services.career.ats_discovery import discover_ats, ATS_SEARCH_PATTERNS
from app.utils.search import discover_urls

async def test_discovery():
    logging.basicConfig(level=logging.INFO)
    company = "Ramp"
    print(f"Testing discovery for: {company}")
    
    urls = await discover_urls(company, ATS_SEARCH_PATTERNS)
    print(f"Discovered URLs: {urls}")
    
    platform, url = await discover_ats(company)
    print(f"Final Detection: Platform={platform}, URL={url}")

if __name__ == "__main__":
    asyncio.run(test_discovery())
