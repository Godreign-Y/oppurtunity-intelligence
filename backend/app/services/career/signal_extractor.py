"""
app/services/career/signal_extractor.py

Extracts structured intelligence signals from raw ATS job listing data.
Maps job roles and tech keywords to pain indicators using the BRD taxonomy.
"""

import re
import logging
from typing import Optional

from app.schemas.signal import UnifiedSignalSchema
from app.utils.normalization import (
    detect_technologies_from_text,
    detect_pain_indicators_from_text,
    CAREER_PAIN_KEYWORD_MAP,
    build_unified_signal,
)

logger = logging.getLogger(__name__)

SENIORITY_PATTERNS: list[tuple[str, str]] = [
    (r"\bstaff\b", "staff"),
    (r"\bprincipal\b", "principal"),
    (r"\bsenior\b|\bsr\.?\b", "senior"),
    (r"\bjunior\b|\bjr\.?\b", "junior"),
    (r"\blead\b", "lead"),
    (r"\bdirector\b", "director"),
    (r"\bvp\b|vice president", "vp"),
    (r"\bmanager\b", "manager"),
]


def infer_seniority(title: str) -> Optional[str]:
    """
    Infer seniority level from a job title string.

    Args:
        title: Job title text.

    Returns:
        Seniority label string, or None.
    """
    lower = title.lower()
    for pattern, label in SENIORITY_PATTERNS:
        if re.search(pattern, lower):
            return label
    return "mid"


def extract_signal_from_greenhouse_job(
    job: dict, company_name: str
) -> Optional[UnifiedSignalSchema]:
    """
    Convert a raw Greenhouse job dict into a UnifiedSignalSchema.

    Args:
        job: Raw job dict from the Greenhouse API.
        company_name: Name of the company.

    Returns:
        UnifiedSignalSchema or None if the job has insufficient data.
    """
    title: str = job.get("title", "")
    if not title:
        return None

    departments: list[dict] = job.get("departments", [])
    department: str = departments[0].get("name", "") if departments else ""
    location: str = ""
    offices = job.get("offices", [])
    if offices:
        location = offices[0].get("name", "")

    combined_text = f"{title} {department} {location}"
    technologies = detect_technologies_from_text(combined_text)

    # Also check title against career pain keyword map
    pain_from_title: list[str] = []
    lower_title = title.lower()
    for kw, pain in CAREER_PAIN_KEYWORD_MAP.items():
        if kw in lower_title and pain not in pain_from_title:
            pain_from_title.append(pain)

    pain_from_text = detect_pain_indicators_from_text(combined_text)
    pain_indicators = list(set(pain_from_title + pain_from_text))

    seniority = infer_seniority(title)
    source_url = job.get("absolute_url", "")
    timestamp = job.get("updated_at", "")
    evidence = [f"Job posting: {title}"]
    
    # Determine urgency based on keywords in title or timestamp
    urgency = "Medium"
    if any(w in lower_title for w in ["urgent", "immediate", "critical", "staffing", "asap"]):
        urgency = "High"

    if location:
        evidence.append(f"Location: {location}")

    confidence = 0.6 + (0.1 if len(technologies) > 2 else 0.0)

    return build_unified_signal(
        company_name=company_name,
        source_type="career_page",
        event_type="hiring_signal",
        technologies=technologies,
        pain_indicators=pain_indicators,
        evidence=evidence,
        source_url=source_url,
        role_title=title,
        department=department,
        seniority=seniority,
        location=location,
        urgency=urgency,
        timestamp=timestamp,
        confidence=min(confidence, 0.95),
    )



def extract_signal_from_lever_job(
    job: dict, company_name: str
) -> Optional[UnifiedSignalSchema]:
    """
    Convert a raw Lever job dict into a UnifiedSignalSchema.

    Args:
        job: Raw job dict from the Lever API.
        company_name: Name of the company.

    Returns:
        UnifiedSignalSchema or None if the job has insufficient data.
    """
    title: str = job.get("text", "")
    if not title:
        return None

    categories: dict = job.get("categories", {})
    department: str = categories.get("team", "") or categories.get("department", "")
    location: str = categories.get("location", "")
    commitment: str = categories.get("commitment", "")

    # Lever jobs have a plainText description field
    description: str = job.get("descriptionPlain", "") or ""
    combined_text = f"{title} {department} {description[:500]}"

    technologies = detect_technologies_from_text(combined_text)
    pain_from_text = detect_pain_indicators_from_text(combined_text)

    pain_from_title: list[str] = []
    lower_title = title.lower()
    for kw, pain in CAREER_PAIN_KEYWORD_MAP.items():
        if kw in lower_title and pain not in pain_from_title:
            pain_from_title.append(pain)

    pain_indicators = list(set(pain_from_title + pain_from_text))
    seniority = infer_seniority(title)
    source_url = job.get("hostedUrl", "")
    timestamp = str(job.get("createdAt", ""))
    evidence = [f"Job posting: {title}"]
    
    urgency = "Medium"
    if any(w in lower_title for w in ["urgent", "immediate", "critical", "staffing", "asap"]):
        urgency = "High"

    if location:
        evidence.append(f"Location: {location}")

    confidence = 0.62 + (0.1 if len(technologies) > 2 else 0.0)

    return build_unified_signal(
        company_name=company_name,
        source_type="career_page",
        event_type="hiring_signal",
        technologies=technologies,
        pain_indicators=pain_indicators,
        evidence=evidence,
        source_url=source_url,
        role_title=title,
        department=department,
        seniority=seniority,
        location=location,
        urgency=urgency,
        timestamp=timestamp,
        confidence=min(confidence, 0.95),
    )


def extract_signals_from_generic_jobs(
    jobs: list[dict], company_name: str
) -> list[UnifiedSignalSchema]:
    """
    Convert a list of generic job dicts (Ashby/Workday) into signals.

    Args:
        jobs: List of simplified job dicts with at least a 'title' key.
        company_name: Name of the company.

    Returns:
        List of UnifiedSignalSchema instances.
    """
    signals: list[UnifiedSignalSchema] = []
    for job in jobs:
        title = job.get("title", "")
        if not title:
            continue

        technologies = detect_technologies_from_text(title)
        pain_indicators = detect_pain_indicators_from_text(title)

        pain_from_title: list[str] = []
        lower_title = title.lower()
        for kw, pain in CAREER_PAIN_KEYWORD_MAP.items():
            if kw in lower_title and pain not in pain_from_title:
                pain_from_title.append(pain)

        pain_indicators = list(set(pain_indicators + pain_from_title))
        seniority = infer_seniority(title)

        signal = build_unified_signal(
            company_name=company_name,
            source_type="career_page",
            event_type="hiring_signal",
            technologies=technologies,
            pain_indicators=pain_indicators,
            evidence=[f"Job posting: {title}"],
            source_url=job.get("url"),
            role_title=title,
            seniority=seniority,
            confidence=0.55,
        )
        signals.append(signal)

    return signals
