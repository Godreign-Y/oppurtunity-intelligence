"""
app/utils/normalization.py

Utility functions for normalizing extracted data into the Unified Signal Schema.
All sources (career pages, engineering blogs) must pass through this layer.
"""

from datetime import datetime, timezone
from typing import Optional

from app.schemas.signal import UnifiedSignalSchema

# Pain indicator keyword mapping from the BRD
CAREER_PAIN_KEYWORD_MAP: dict[str, str] = {
    "kubernetes": "infra_scaling",
    "terraform": "cloud_automation",
    "observability": "monitoring_gaps",
    "ci/cd": "deployment_complexity",
    "cicd": "deployment_complexity",
    "distributed systems": "scaling_pressure",
    "sre": "reliability_pressure",
    "ai engineer": "ai_initiative",
    "security engineer": "security_pressure",
    "platform engineer": "infra_scaling",
    "mlops": "ai_initiative",
    "data engineer": "data_scaling",
}

BLOG_PAIN_TAXONOMY: dict[str, list[str]] = {
    "scaling_pressure": [
        "scaling", "growth", "traffic spike", "load", "capacity", "sharding",
        "distributed", "horizontal scaling", "vertical scaling",
    ],
    "deployment_complexity": [
        "deployment", "ci/cd", "pipeline", "release", "rollback",
        "blue-green", "canary", "gitops",
    ],
    "cloud_cost_pressure": [
        "cost", "spend", "billing", "savings", "optimization", "rightsizing",
        "reserved instances", "spot instances",
    ],
    "reliability_issues": [
        "outage", "incident", "downtime", "sla", "slo", "reliability",
        "latency", "p99", "uptime",
    ],
    "legacy_modernization": [
        "migration", "rewrite", "refactor", "monolith", "legacy",
        "modernization", "strangler fig",
    ],
    "ai_adoption_uncertainty": [
        "llm", "genai", "generative ai", "ai integration", "ml model",
        "mlops", "vector database", "embeddings",
    ],
    "security_pressure": [
        "security", "compliance", "soc2", "gdpr", "vulnerability",
        "penetration testing", "zero trust", "iam",
    ],
}


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
    Extract technology keywords from text via a curated list.

    Args:
        text: Lowercased content string.

    Returns:
        List of recognized technology names found in text.
    """
    tech_keywords = [
        "kubernetes", "k8s", "terraform", "aws", "gcp", "azure",
        "kafka", "redis", "postgresql", "mysql", "mongodb", "elasticsearch",
        "docker", "grafana", "prometheus", "datadog", "opentelemetry",
        "airflow", "spark", "flink", "dbt", "snowflake", "bigquery",
        "fastapi", "django", "flask", "rails", "nodejs", "go", "rust",
        "python", "java", "typescript", "react", "next.js", "graphql",
        "grpc", "rabbitmq", "celery", "istio", "envoy", "nginx",
    ]
    lower = text.lower()
    return [tech for tech in tech_keywords if tech in lower]


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
