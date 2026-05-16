"""
app/services/blog/signal_extractor.py

Extracts structured intelligence signals from engineering blog articles.
Uses the BRD pain detection taxonomy to identify operational challenges.
"""

import logging
from typing import Optional

from app.schemas.signal import UnifiedSignalSchema
from app.utils.normalization import (
    detect_technologies_from_text,
    detect_pain_indicators_from_text,
    build_unified_signal,
)

logger = logging.getLogger(__name__)

ARCHITECTURE_TERMS: list[str] = [
    "microservices", "monolith", "event-driven", "cqrs", "saga",
    "service mesh", "api gateway", "grpc", "serverless", "edge computing",
]

MIGRATION_TERMS: list[str] = [
    "migration", "rewrite", "refactor", "modernization", "lift and shift",
    "strangler fig", "decomposition",
]

SCALING_TERMS: list[str] = [
    "scaling", "horizontal", "vertical", "autoscaling", "load balancing",
    "sharding", "partitioning", "replication",
]

AI_TERMS: list[str] = [
    "llm", "large language model", "rag", "embeddings", "vector",
    "generative ai", "genai", "fine-tuning", "mlops", "inference",
]


def detect_topics_from_text(text: str) -> list[str]:
    """
    Detect blog topic categories from article text.

    Args:
        text: Lowercased article content.

    Returns:
        List of topic category strings.
    """
    lower = text.lower()
    topics: list[str] = []

    if any(t in lower for t in ARCHITECTURE_TERMS):
        topics.append("architecture_evolution")
    if any(t in lower for t in MIGRATION_TERMS):
        topics.append("migration_or_modernization")
    if any(t in lower for t in SCALING_TERMS):
        topics.append("scaling_engineering")
    if any(t in lower for t in AI_TERMS):
        topics.append("ai_adoption")

    return topics


def infer_event_type(pain_indicators: list[str], topics: list[str]) -> str:
    """
    Infer the most appropriate event type label from pain indicators and topics.

    Args:
        pain_indicators: List of detected pain category strings.
        topics: List of detected topic category strings.

    Returns:
        Event type label string.
    """
    if "legacy_modernization" in pain_indicators or "migration_or_modernization" in topics:
        return "infra_modernization"
    if "scaling_pressure" in pain_indicators or "scaling_engineering" in topics:
        return "scaling_challenge"
    if "ai_adoption_uncertainty" in pain_indicators or "ai_adoption" in topics:
        return "ai_adoption"
    if "reliability_issues" in pain_indicators:
        return "reliability_incident"
    if "deployment_complexity" in pain_indicators:
        return "deployment_optimization"
    return "engineering_insight"


def extract_evidence_snippets(text: str, max_snippets: int = 5) -> list[str]:
    """
    Extract short evidence snippets from article text.

    Args:
        text: Full article content.
        max_snippets: Maximum number of snippets to return.

    Returns:
        List of sentence-like evidence strings.
    """
    sentences = [s.strip() for s in text.replace("\n", " ").split(". ") if len(s.strip()) > 30]
    return sentences[:max_snippets]


def extract_signal_from_article(
    title: str,
    content: str,
    url: str,
    company_name: str,
) -> Optional[UnifiedSignalSchema]:
    """
    Extract a normalized signal from a single blog article.

    Args:
        title: Article title.
        content: Full article markdown content.
        url: Article URL.
        company_name: Name of the company.

    Returns:
        UnifiedSignalSchema or None if the article has insufficient signal.
    """
    if not content or len(content) < 100:
        return None

    combined = f"{title} {content}"
    technologies = detect_technologies_from_text(combined)
    pain_indicators = detect_pain_indicators_from_text(combined)
    topics = detect_topics_from_text(combined)
    evidence = extract_evidence_snippets(content)

    if not pain_indicators and not topics:
        logger.debug(f"No signals found in article: {title}")
        return None

    event_type = infer_event_type(pain_indicators, topics)

    # Confidence: more signals → higher confidence
    base = 0.5
    base += min(len(technologies) * 0.05, 0.2)
    base += min(len(pain_indicators) * 0.05, 0.2)
    confidence = min(base, 0.95)

    return build_unified_signal(
        company_name=company_name,
        source_type="engineering_blog",
        event_type=event_type,
        technologies=technologies,
        pain_indicators=pain_indicators,
        evidence=evidence,
        source_url=url,
        topics=topics,
        confidence=confidence,
    )
