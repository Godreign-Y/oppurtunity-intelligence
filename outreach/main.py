"""Main entry point for testing the data pipeline.

This script fetches raw job data and processes it through the pipeline,
printing the results for verification.
"""

import asyncio

from fetcher import fetch_jobs
from processor import process_jobs
from enrichment import find_decision_makers
from schemas import EnrichedOpportunity


def extract_domain(company_name: str) -> str:
    """Extracts a clean domain name from a company name.

    Args:
        company_name (str): The raw company name.

    Returns:
        str: A simplified domain string (e.g., 'technova.com').
    """
    clean_name = company_name.lower().replace(" ", "")
    return f"{clean_name}.com"


async def main() -> None:
    """Runs the data extraction, transformation, and enrichment pipeline.

    Fetches jobs, processes them, and then enriches the first job with
    decision maker data from the Apollo API.
    """
    print("Fetching jobs...")
    try:
        raw_jobs = await fetch_jobs()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to fetch jobs: {e}")
        return

    print(f"Fetched {len(raw_jobs)} jobs. Processing...")
    processed_jobs = process_jobs(raw_jobs)
    
    if not processed_jobs:
        print("No jobs to process.")
        return
        
    print("Enriching the first opportunity...")
    first_job = processed_jobs[0]
    domain: str = extract_domain(first_job.company_name)
    
    target_departments = ["it"]
        
    print(f"Found domain: {domain}, searching for departments: {target_departments}")
    decision_makers = await find_decision_makers(domain, target_departments)
    
    enriched_job = EnrichedOpportunity(
        **first_job.model_dump(),
        company_domain=domain,
        decision_makers=decision_makers
    )
    
    print("\nEnriched Opportunity (JSON):")
    print(enriched_job.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
