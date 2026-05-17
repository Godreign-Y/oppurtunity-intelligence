"""
app/services/hiring/service.py

Orchestrates the Hiring Signals data collection, processing, and database transaction pipeline.
"""

import logging
from typing import List, Dict
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.hiring_signal import HiringSignal
from app.services.company_service import get_or_create_company
from app.services.hiring.fetcher import fetch_jobs
from app.services.hiring.processor import sanitize_text, extract_tech_stack
from app.config.category_mapper import map_to_opportunity_category

logger = logging.getLogger(__name__)


class HiringService:
    """
    Service layer to query and ingest hiring indicators.
    """

    @staticmethod
    def get_recent_hiring_signals(db: Session, limit: int = 50) -> List[HiringSignal]:
        """Get recent job postings / hiring signals."""
        return db.query(HiringSignal).order_by(HiringSignal.created_at.desc()).limit(limit).all()

    @staticmethod
    async def run_hiring_pipeline(db: Session) -> Dict:
        """
        Runs the job postings extraction and sanitization pipeline.
        Queries Google Jobs, cleans HTML, matches tech keywords,
        associates target accounts, and persists database signals.
        """
        logger.info("[HiringPipeline] Starting Hiring signals discovery pipeline...")
        
        try:
            raw_jobs = await fetch_jobs()
        except Exception as e:
            logger.error(f"[HiringPipeline] Job fetch failure: {e}")
            return {"status": "error", "message": str(e), "total_ingested": 0}

        logger.info(f"[HiringPipeline] Fetched {len(raw_jobs)} job postings. Processing and saving...")

        total_ingested = 0
        ingested_jobs = []

        for job in raw_jobs:
            try:
                sanitized_desc = sanitize_text(job.raw_description)
                detected_stack = extract_tech_stack(sanitized_desc)

                # Find or create company Target
                company = get_or_create_company(db, job.company_name)

                # Persist hiring signal
                hiring_signal = HiringSignal(
                    company_id=company.id,
                    job_title=job.job_title,
                    posted_date=job.posted_date,
                    sanitized_description=sanitized_desc,
                    detected_tech_stack=detected_stack,
                    source_url=job.source_url,
                    opportunity_category=map_to_opportunity_category(
                        "mlops_scaling"
                        if any(t.lower() in {"mlops", "pytorch", "tensorflow", "mlflow"} for t in detected_stack)
                        else "deployment_complexity"
                    ),
                )
                db.add(hiring_signal)
                db.commit()
                db.refresh(hiring_signal)

                total_ingested += 1
                ingested_jobs.append({
                    "company_name": job.company_name,
                    "job_title": job.job_title,
                    "tech_stack": detected_stack
                })
                logger.info(f"[HiringPipeline] Saved hiring signal: {job.job_title} at {job.company_name}")

            except Exception as e:
                logger.error(f"[HiringPipeline] Failed to process job signal: {e}")
                continue

        return {
            "status": "success",
            "message": f"Hiring pipeline completed. Ingested {total_ingested} job postings.",
            "total_ingested": total_ingested,
            "jobs": ingested_jobs
        }
