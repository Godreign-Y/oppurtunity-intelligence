"""
app/pipelines/hiring_signals_pipeline.py

Standalone Hiring Signals Intelligence Pipeline.

Fetches real job postings (Google Jobs via SerpApi or high-fidelity simulation),
filters by company name, maps tech stacks to opportunity categories,
and persists records to the database.

Entry point: run_hiring_signals_pipeline(company_name, db)
"""

import logging
from typing import Any
from sqlalchemy.orm import Session

from app.services.hiring.fetcher import fetch_jobs
from app.services.hiring.processor import sanitize_text, extract_tech_stack
from app.services.company_service import get_or_create_company
from app.models.hiring_signal import HiringSignal
from app.config.category_mapper import map_to_opportunity_category
from app.config.keywords.career_pain_keywords import CAREER_PAIN_KEYWORD_MAP

logger = logging.getLogger(__name__)

# Tech-to-pain-type mapping specific to hiring signals.
# Maps detected tech stack items → internal pain type → opportunity category.
HIRING_TECH_TO_PAIN: dict[str, str] = {
    "kubernetes": "infra_scaling",
    "docker": "infra_scaling",
    "terraform": "cloud_automation",
    "aws": "cloud_migration",
    "gcp": "cloud_migration",
    "azure": "cloud_migration",
    "pytorch": "mlops_scaling",
    "tensorflow": "mlops_scaling",
    "mlflow": "mlops_scaling",
    "airflow": "data_pipeline_failure",
    "kafka": "scaling_pressure",
    "react": "deployment_complexity",
    "fastapi": "deployment_complexity",
    "llm": "ai_initiative",
    "langchain": "ai_initiative",
}


def _infer_category_from_tech_stack(tech_stack: list[str], job_title: str) -> str:
    """
    Infer the opportunity category from a job's detected tech stack and title.

    Checks the tech stack items against HIRING_TECH_TO_PAIN, then falls back
    to CAREER_PAIN_KEYWORD_MAP for title-based inference.

    Args:
        tech_stack: List of detected technology names from job description.
        job_title: Job title string.

    Returns:
        A canonical opportunity category string.
    """
    for tech in tech_stack:
        pain = HIRING_TECH_TO_PAIN.get(tech.lower())
        if pain:
            return map_to_opportunity_category(pain)

    lower_title = job_title.lower()
    for kw, pain in CAREER_PAIN_KEYWORD_MAP.items():
        if kw in lower_title:
            return map_to_opportunity_category(pain)

    return map_to_opportunity_category("deployment_complexity")


async def run_hiring_signals_pipeline(
    company_name: str,
    db: Session,
) -> list[dict[str, Any]]:
    """
    Run the Hiring Signals Intelligence Pipeline for a specific company.

    Fetches job postings, filters by company name, maps to opportunity categories,
    and persists records to the database.

    Args:
        company_name: Target company to analyze hiring signals for.
        db: Active SQLAlchemy database session.

    Returns:
        List of enriched hiring signal dicts with opportunity_category field.
    """
    logger.info(f"[HiringSignalsPipeline] Starting for company: {company_name}")

    try:
        raw_jobs = await fetch_jobs(company_name)
        logger.info(f"[HiringSignalsPipeline] Fetched {len(raw_jobs)} raw job postings")
    except Exception as exc:
        logger.error(f"[HiringSignalsPipeline] Job fetch failed: {exc}")
        return []

    company = get_or_create_company(db, company_name)
    enriched: list[dict[str, Any]] = []
    company_lower = company_name.lower()

    for job in raw_jobs:
        try:
            if company_lower not in job.company_name.lower():
                logger.info(
                    f"[HiringSignalsPipeline] Skipping unrelated job at {job.company_name}"
                )
                continue

            sanitized_desc = sanitize_text(job.raw_description)
            tech_stack = extract_tech_stack(sanitized_desc)
            category = _infer_category_from_tech_stack(tech_stack, job.job_title)

            # Persist to DB
            signal = HiringSignal(
                company_id=company.id,
                job_title=job.job_title,
                posted_date=job.posted_date,
                sanitized_description=sanitized_desc,
                detected_tech_stack=tech_stack,
                source_url=job.source_url,
                opportunity_category=category,
            )
            db.add(signal)
            db.commit()
            db.refresh(signal)

            enriched.append({
                "id": str(signal.id),
                "job_title": job.job_title,
                "company_name": job.company_name,
                "posted_date": job.posted_date,
                "sanitized_description": sanitized_desc,
                "detected_tech_stack": tech_stack,
                "opportunity_category": category,
                "source": "hiring_signals",
                "source_url": job.source_url,
            })
            logger.info(
                f"[HiringSignalsPipeline] Saved: {job.job_title} → {category}"
            )
        except Exception as exc:
            logger.error(f"[HiringSignalsPipeline] Failed to process job: {exc}")
            continue

    logger.info(
        f"[HiringSignalsPipeline] Completed: {len(enriched)} signals for {company_name}"
    )
    return enriched
