"""Data fetcher module.

This module is responsible for asynchronously fetching job posting data
from the SerpApi Google Jobs endpoint.
"""

import os
from typing import Any, Dict, List

import httpx
from dotenv import load_dotenv

from schemas import RawJobPosting

# Load environment variables from .env file
load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")


async def fetch_jobs() -> List[RawJobPosting]:
    """Fetches job postings from SerpApi.

    Queries the Google Jobs endpoint for product-based company roles
    in specific technical domains (e.g., DevOps, Cloud Migration).
    Parses the JSON response and validates the individual job items
    using the RawJobPosting Pydantic model.

    Returns:
        List[RawJobPosting]: A list of validated job posting objects.
        
    Raises:
        ValueError: If the SERPAPI_API_KEY is not found.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not SERPAPI_API_KEY:
        raise ValueError("SERPAPI_API_KEY environment variable is not set.")

    url = "https://serpapi.com/search"
    query = '("DevOps" OR "Cloud Migration") "product"'
    
    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "hl": "en"
    }

    # SerpApi can sometimes take longer than the default 5 seconds to scrape real-time results
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            # Expose the actual error message from the API (e.g., "Invalid API key")
            raise RuntimeError(f"API Error {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            raise RuntimeError(f"Request Error: {e.__class__.__name__} - {e}") from e
            
        data = response.json()

    validated_jobs: List[RawJobPosting] = []
    jobs_results: List[Dict[str, Any]] = data.get("jobs_results", [])
    
    for job in jobs_results:
        # Extract fields based on the typical SerpApi Google Jobs response structure
        # Use 'or' to fallback if the key exists but its value is None
        title = job.get("title") or "Unknown Title"
        company = job.get("company_name") or "Unknown Company"
        description = job.get("description") or ""
        
        # 'posted_at' might be nested in 'detected_extensions'
        extensions = job.get("detected_extensions") or {}
        posted = extensions.get("posted_at")
        
        job_data = {
            "job_title": title,
            "company_name": company,
            "raw_description": description,
            "posted_date": posted
        }
        
        validated_job = RawJobPosting(**job_data)
        validated_jobs.append(validated_job)

    return validated_jobs
