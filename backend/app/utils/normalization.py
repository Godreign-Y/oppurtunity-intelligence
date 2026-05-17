"""
app/utils/normalization.py

Utility functions for normalizing extracted data into the Unified Signal Schema.
All sources (career pages, engineering blogs) must pass through this layer.

Keywords are sourced from app/config/keywords/ — edit them there, not here.
"""

from datetime import datetime, timezone
from typing import Optional

from app.schemas.signal import UnifiedSignalSchema
from app.config.keywords.career_pain_keywords import CAREER_PAIN_KEYWORD_MAP
from app.config.keywords.blog_pain_keywords import BLOG_PAIN_TAXONOMY
from app.config.keywords.tech_stack_keywords import TECH_STACK_KEYWORDS


def detect_pain_indicators_from_text(text: str) -> list[str]:
    """
    Detect pain indicator categories from free text using keyword matching.

    Args:
        text: Lowercased content to scan.

    Returns:
        Deduplicated list of pain indicator category strings.
    """
    found: set[str] = set()
    lower = text.lower()

    for pain_type, keywords in BLOG_PAIN_TAXONOMY.items():
        for kw in keywords:
            if kw in lower:
                found.add(pain_type)
                break

    return list(found)


def detect_technologies_from_text(text: str) -> list[str]:
    """
    Extract technology keywords from text via the curated TECH_STACK_KEYWORDS list.

    Keywords are defined in app/config/keywords/tech_stack_keywords.py.

    Args:
        text: Content string to scan.

    Returns:
        List of recognized technology names found in text.
    """
    lower = text.lower()
    return [tech for tech in TECH_STACK_KEYWORDS if tech in lower]


def map_pain_to_opportunity(pain_indicators: list[str]) -> list[str]:
    """
    Map detected pain indicators to suggested opportunity types.

    Args:
        pain_indicators: List of pain category strings.

    Returns:
        List of suggested opportunity/service strings.
    """
    mapping: dict[str, str] = {
        "infra_scaling": "Infrastructure Scaling Consulting",
        "cloud_automation": "Cloud Automation & IaC Consulting",
        "monitoring_gaps": "Observability & Monitoring Setup",
        "deployment_complexity": "CI/CD & DevOps Consulting",
        "scaling_pressure": "Distributed Systems Architecture",
        "reliability_pressure": "SRE & Reliability Engineering",
        "ai_initiative": "AI/ML Integration Services",
        "security_pressure": "Security & Compliance Consulting",
        "cloud_cost_pressure": "Cloud Cost Optimization",
        "reliability_issues": "Reliability Engineering & Incident Response",
        "legacy_modernization": "Cloud Migration & Modernization",
        "ai_adoption_uncertainty": "GenAI Integration & MLOps",
        "data_scaling": "Data Engineering & Platform Services",
    }
    seen: set[str] = set()
    result: list[str] = []
    for pain in pain_indicators:
        opp = mapping.get(pain)
        if opp and opp not in seen:
            result.append(opp)
            seen.add(opp)
    return result


def build_unified_signal(
    company_name: str,
    source_type: str,
    event_type: str,
    technologies: list[str],
    pain_indicators: list[str],
    evidence: list[str],
    source_url: Optional[str] = None,
    topics: Optional[list[str]] = None,
    role_title: Optional[str] = None,
    department: Optional[str] = None,
    seniority: Optional[str] = None,
    location: Optional[str] = None,
    urgency: str = "Medium",
    timestamp: Optional[str] = None,
    confidence: float = 0.5,
) -> UnifiedSignalSchema:
    """
    Construct a UnifiedSignalSchema from normalized components.
    ...
    """
    opportunity_mapping = map_pain_to_opportunity(pain_indicators)
    business_implications = [
        f"Operational pressure around: {pain.replace('_', ' ')}"
        for pain in pain_indicators
    ]

    return UnifiedSignalSchema(
        company_name=company_name,
        source_type=source_type,
        event_type=event_type,
        technologies=technologies,
        topics=topics or [],
        pain_indicators=pain_indicators,
        business_implications=business_implications,
        opportunity_mapping=opportunity_mapping,
        confidence=confidence,
        evidence=evidence,
        source_url=source_url,
        timestamp=timestamp or datetime.now(timezone.utc).isoformat(),
        role_title=role_title,
        department=department,
        seniority=seniority,
        location=location,
        urgency=urgency,
    )
