"""
app/services/funding/service.py

Orchestrates the Funding Signals data collection, classification, and persistence pipeline.
"""

import logging
import asyncio
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.company import Company
from app.models.funding_event import FundingEvent
from app.services.company_service import get_or_create_company
from app.services.funding.rss_fetcher import RSSFetcher
from app.services.funding.llm_extractor import LLMExtractor
from app.services.funding.classifier import CompanyClassifier
from app.config.category_mapper import map_to_opportunity_category

logger = logging.getLogger(__name__)


def infer_funding_opportunity_category(stage: str | None, amount: float | None) -> str:
    """Map funding context to one canonical opportunity category."""
    stage_lower = (stage or "").lower()
    if "seed" in stage_lower or "pre-seed" in stage_lower:
        return map_to_opportunity_category("cloud_migration")
    if "series a" in stage_lower:
        return map_to_opportunity_category("scaling_bottleneck")
    if "series b" in stage_lower:
        return map_to_opportunity_category("deployment_failure")
    if "series c" in stage_lower or "series d" in stage_lower:
        return map_to_opportunity_category("ai_ml_production_pain")
    if amount and amount >= 50:
        return map_to_opportunity_category("ai_ml_production_pain")
    if amount and amount >= 20:
        return map_to_opportunity_category("scaling_bottleneck")
    return map_to_opportunity_category("cloud_migration")


class FundingService:
    """
    Service layer to query and ingest startup funding rounds.
    """

    @staticmethod
    def get_recent_funding_events(db: Session, limit: int = 50) -> List[FundingEvent]:
        """Get recent corporate funding round logs."""
        return db.query(FundingEvent).order_by(FundingEvent.date.desc()).limit(limit).all()

    @staticmethod
    async def run_funding_pipeline(db: Session) -> Dict:
        """
        Runs the async data extraction and transformation pipeline.
        Fetches RSS feeds, extracts company/round details using LLM,
        checks SaaS classification, and saves valid funding events.
        """
        logger.info("[FundingPipeline] Starting Funding round discovery pipeline...")
        fetcher = RSSFetcher()
        extractor = LLMExtractor()
        classifier = CompanyClassifier()

        try:
            raw_signals = await fetcher.fetch_signals()
        except Exception as e:
            logger.error(f"[FundingPipeline] Failed to fetch signals: {e}")
            return {"status": "error", "message": str(e), "total_ingested": 0}

        logger.info(f"[FundingPipeline] Fetched {len(raw_signals)} potential signals. Filtering & Extracting...")
        
        total_ingested = 0
        ingested_events = []

        for signal in raw_signals:
            try:
                # Rate limit safety
                await asyncio.sleep(0.5)

                extracted = await extractor.extract_entities(signal["raw_text"])
                if not extracted or not extracted.get("company_name"):
                    continue

                company_name = extracted["company_name"].strip()
                amount = extracted.get("amount")
                stage = extracted.get("stage") or "Seed"

                # Check SaaS/Product status
                is_product = await classifier.classify_company(company_name, signal["raw_text"])
                if not is_product:
                    logger.info(f"[FundingPipeline] Discarding service company: {company_name}")
                    continue

                # Database target account creation
                company = get_or_create_company(db, company_name)
                
                # Calculate composite opportunity score
                # Base 10 + 20 (if Series round) + 15 (if amount > $10M)
                opportunity_score = 10
                if stage and "Series" in stage:
                    opportunity_score += 20
                if amount and amount > 10.0:
                    opportunity_score += 15

                # Create funding event
                funding_event = FundingEvent(
                    company_id=company.id,
                    amount=amount,
                    stage=stage,
                    source_url=signal["source_url"],
                    raw_text=signal["raw_text"],
                    opportunity_score=opportunity_score,
                    opportunity_category=infer_funding_opportunity_category(stage, amount),
                )
                db.add(funding_event)
                db.commit()
                db.refresh(funding_event)

                total_ingested += 1
                ingested_events.append({
                    "company_name": company_name,
                    "amount": amount,
                    "stage": stage,
                    "score": opportunity_score,
                    "source_url": signal["source_url"],
                    "raw_text": signal["raw_text"],
                    "opportunity_category": funding_event.opportunity_category,
                })
                logger.info(f"[FundingPipeline] Saved funding event for {company_name} (${amount}M, Score: {opportunity_score})")

            except Exception as e:
                logger.error(f"[FundingPipeline] Error processing signal: {e}")
                continue

        return {
            "status": "success",
            "message": f"Pipeline execution completed. Ingested {total_ingested} funding signals.",
            "total_ingested": total_ingested,
            "events": ingested_events
        }
