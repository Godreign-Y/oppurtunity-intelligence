"""
app/services/hiring/fetcher.py

Fetches job posting data from SerpApi Google Jobs endpoint,
with a robust local simulation fallback if no API key is set.
"""

import logging
import httpx
from typing import List, Dict

from app.core.config import settings

logger = logging.getLogger(__name__)


class RawJobPosting:
    def __init__(self, job_title: str, company_name: str, raw_description: str, posted_date: str = None):
        self.job_title = job_title
        self.company_name = company_name
        self.raw_description = raw_description
        self.posted_date = posted_date or "Recently"


async def fetch_jobs() -> List[RawJobPosting]:
    """
    Fetches job postings from SerpApi Google Jobs.
    Falls back to high-fidelity simulated job postings if SERPAPI_API_KEY is not set.
    """
    api_key = settings.serpapi_api_key

    if not api_key:
        logger.warning("[HiringFetcher] SERPAPI_API_KEY is not set. Using offline high-fidelity job simulation.")
        return get_simulated_jobs()

    url = "https://serpapi.com/search"
    query = '("DevOps" OR "Cloud Migration" OR "Kubernetes") "product"'
    
    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": api_key,
        "hl": "en"
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            jobs_results = data.get("jobs_results", [])
            validated_jobs: List[RawJobPosting] = []

            for job in jobs_results:
                title = job.get("title") or "Unknown Title"
                company = job.get("company_name") or "Unknown Company"
                description = job.get("description") or ""
                extensions = job.get("detected_extensions") or {}
                posted = extensions.get("posted_at") or "Recently"

                validated_jobs.append(RawJobPosting(
                    job_title=title,
                    company_name=company,
                    raw_description=description,
                    posted_date=posted
                ))
            
            logger.info(f"[HiringFetcher] Successfully fetched {len(validated_jobs)} real job listings from SerpApi.")
            return validated_jobs

    except Exception as e:
        logger.error(f"[HiringFetcher] SerpApi query failed: {e}. Falling back to offline simulation.")
        return get_simulated_jobs()


def get_simulated_jobs() -> List[RawJobPosting]:
    """Generates premium simulated jobs mapping tech stack requirements for leading product companies."""
    return [
        RawJobPosting(
            job_title="Senior DevOps & Infrastructure Engineer",
            company_name="CloudScale AI",
            raw_description=(
                "<p>We are seeking a senior engineer to drive our Kubernetes cloud migration. "
                "Our current tech stack is hosted on legacy AWS virtual machines, and we are modernizing "
                "our infrastructure with Docker, CI/CD automation pipelines, Python microservices, and Terraform. "
                "Experience with Azure or GCP is a plus.</p>"
            ),
            posted_date="2 days ago"
        ),
        RawJobPosting(
            job_title="Cloud Migration Specialist",
            company_name="VeloSaaS Technologies",
            raw_description=(
                "Join us as we move our flagship SaaS product from on-prem legacy servers "
                "to modern Kubernetes containers on Azure. We need expert CI/CD pipelines, "
                "Node.js API services modernization, React frontend styling, and Docker containers security management."
            ),
            posted_date="1 week ago"
        ),
        RawJobPosting(
            job_title="Infrastructure Platform Engineer",
            company_name="Aura Analytics",
            raw_description=(
                "Help modernization teams architect and scale microservices. "
                "We need strong knowledge of Python, GCP Cloud Run, Docker containers, Kubernetes clusters, "
                "and legacy server refactoring. Continuous integration and delivery (CI/CD) is essential."
            ),
            posted_date="4 hours ago"
        ),
        RawJobPosting(
            job_title="Legacy Systems Modernization Engineer",
            company_name="Apex Enterprise",
            raw_description=(
                "We are refactoring our core monolithic platform. The candidate will help with CI/CD implementation, "
                "Docker image builder configurations, AWS RDS deployments, and transition from legacy monoliths "
                "to Dockerized microservices."
            ),
            posted_date="3 days ago"
        )
    ]
