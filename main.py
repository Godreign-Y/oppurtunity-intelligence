"""Main entry point for testing the data pipeline.

This script fetches raw job data and processes it through the pipeline,
printing the results for verification.
"""

import asyncio

from fetcher import fetch_jobs
from processor import process_jobs


async def main() -> None:
    """Runs the data extraction and transformation pipeline.

    Fetches jobs from the configured API and processes them to remove HTML
    and extract relevant tech stack keywords. Prints the first two processed
    jobs to standard output.
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
    
    print("First 2 processed jobs:")
    for job in processed_jobs[:2]:
        # Using Pydantic's built-in JSON dumping for clean output
        print(job.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
