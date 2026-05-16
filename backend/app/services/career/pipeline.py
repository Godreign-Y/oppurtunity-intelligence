"""
app/services/career/pipeline.py

Orchestrates the full career page intelligence pipeline:
  1. Discover ATS platform
  2. Extract job listings
  3. Generate normalized signals
"""

import logging
from typing import Optional

from app.services.career.ats_discovery import discover_ats
from app.services.career.ats_extractor import (
    extract_greenhouse_jobs,
    extract_lever_jobs,
    extract_ashby_jobs,
    extract_workday_jobs,
    infer_slug_from_url,
)
from app.services.career.signal_extractor import (
    extract_signal_from_greenhouse_job,
    extract_signal_from_lever_job,
    extract_signals_from_generic_jobs,
)
from app.schemas.signal import UnifiedSignalSchema

logger = logging.getLogger(__name__)


async def run_career_pipeline(
    company_name: str,
) -> tuple[list[UnifiedSignalSchema], Optional[str], Optional[str]]:
    """
    Run the full career page intelligence pipeline for a company.

    Steps:
      1. Discover ATS platform via web search.
      2. Infer the company slug from the discovered URL.
      3. Fetch job listings from the appropriate ATS API.
      4. Extract normalized signals from job listings.

    Args:
        company_name: Name of the company to analyze.

    Returns:
        Tuple of:
          - list of UnifiedSignalSchema instances
          - detected ATS platform name (or None)
          - detected ATS URL (or None)
    """
    logger.info(f"[CareerPipeline] Starting for: {company_name}")

    ats_platform, ats_url = await discover_ats(company_name)

    if not ats_platform or not ats_url:
        logger.warning(f"[CareerPipeline] No ATS found for {company_name}")
        return [], None, None

    slug = infer_slug_from_url(ats_url, ats_platform)

    if not slug:
        logger.warning(
            f"[CareerPipeline] Could not infer slug from URL: {ats_url}"
        )
        return [], ats_platform, ats_url

    signals: list[UnifiedSignalSchema] = []

    if ats_platform == "greenhouse":
        jobs = await extract_greenhouse_jobs(slug)
        for job in jobs:
            signal = extract_signal_from_greenhouse_job(job, company_name)
            if signal:
                signals.append(signal)

    elif ats_platform == "lever":
        jobs = await extract_lever_jobs(slug)
        for job in jobs:
            signal = extract_signal_from_lever_job(job, company_name)
            if signal:
                signals.append(signal)

    elif ats_platform == "ashby":
        jobs = await extract_ashby_jobs(slug)
        signals = extract_signals_from_generic_jobs(jobs, company_name)

    elif ats_platform == "workday":
        jobs = await extract_workday_jobs(slug)
        signals = extract_signals_from_generic_jobs(jobs, company_name)

    # Filter for last 30 days if timestamp exists
    from datetime import datetime, timezone, timedelta
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    recent_signals = []
    for s in signals:
        if s.timestamp:
            try:
                # Handle ISO format strings (with or without Z)
                ts_str = s.timestamp.replace("Z", "+00:00")
                parsed_time = datetime.fromisoformat(ts_str)
                if parsed_time.tzinfo is None:
                    parsed_time = parsed_time.replace(tzinfo=timezone.utc)
                if parsed_time >= thirty_days_ago:
                    recent_signals.append(s)
            except ValueError:
                # If parsing fails, keep it to be safe
                recent_signals.append(s)
        else:
            # If no timestamp is provided, assume it's current
            recent_signals.append(s)
            
    # Prioritize: sort by confidence descending, take top 10
    recent_signals.sort(key=lambda x: x.confidence, reverse=True)
    top_signals = recent_signals[:10]

    logger.info(
        f"[CareerPipeline] {len(signals)} extracted -> {len(recent_signals)} recent -> {len(top_signals)} prioritized for {company_name}"
    )
    return top_signals, ats_platform, ats_url
