"""
app/services/market_pain/capability_mapper.py

Phase 7 — CRITICAL module.
Maps detected market pain to internal organizational capabilities.
Connects community frustrations to Relanto's service practices.

Pain → Technologies → Practices → Accelerators → Internal Strengths
"""

import logging

from app.services.market_pain.schemas import CapabilityMatch

logger = logging.getLogger(__name__)

# Internal organizational capability registry
# Maps pain categories to Relanto practices, accelerators, and strengths
CAPABILITY_REGISTRY: dict[str, dict] = {
    "enterprise_reliability": {
        "practices": [
            "Digital Transformation",
            "Cloud & Infrastructure",
            "SRE & Reliability Engineering",
        ],
        "accelerators": ["R-Optimizer", "R-SmartAssist"],
        "technologies": ["kubernetes", "terraform", "datadog", "grafana", "prometheus"],
        "fit_weight": 0.95,
    },
    "scaling_bottleneck": {
        "practices": [
            "Cloud & Infrastructure",
            "Data & AI",
            "Digital Transformation",
        ],
        "accelerators": ["R-Optimizer"],
        "technologies": ["kubernetes", "kafka", "redis", "aws", "gcp"],
        "fit_weight": 0.90,
    },
    "deployment_failure": {
        "practices": [
            "DevOps & Automation",
            "Cloud & Infrastructure",
            "Digital Transformation",
        ],
        "accelerators": ["R-Optimizer"],
        "technologies": ["terraform", "kubernetes", "docker", "github actions", "argocd"],
        "fit_weight": 0.85,
    },
    "migration_pain": {
        "practices": [
            "Digital Transformation",
            "Cloud & Infrastructure",
            "Application Modernization",
        ],
        "accelerators": ["R-Optimizer", "R-SmartAssist"],
        "technologies": ["kubernetes", "terraform", "aws", "azure", "gcp"],
        "fit_weight": 0.90,
    },
    "security_compliance_gap": {
        "practices": [
            "Cybersecurity & Compliance",
            "Cloud & Infrastructure",
            "Digital Transformation",
        ],
        "accelerators": ["R-SmartAssist"],
        "technologies": ["vault", "terraform", "kubernetes"],
        "fit_weight": 0.90,
    },
    "observability_blindness": {
        "practices": [
            "SRE & Reliability Engineering",
            "Cloud & Infrastructure",
            "DevOps & Automation",
        ],
        "accelerators": ["R-Optimizer"],
        "technologies": ["datadog", "grafana", "prometheus", "opentelemetry"],
        "fit_weight": 0.85,
    },
    "integration_friction": {
        "practices": [
            "Enterprise Integration",
            "Salesforce Practice",
            "Digital Transformation",
        ],
        "accelerators": ["R-SmartAssist"],
        "technologies": ["graphql", "grpc", "kafka", "rabbitmq"],
        "fit_weight": 0.80,
    },
    "data_pipeline_failure": {
        "practices": [
            "Data & AI",
            "Data Engineering",
            "Cloud & Infrastructure",
        ],
        "accelerators": ["R-Optimizer"],
        "technologies": ["kafka", "airflow", "dbt", "spark", "snowflake", "bigquery"],
        "fit_weight": 0.90,
    },
    "ai_ml_production_pain": {
        "practices": [
            "AI First Lab",
            "Data & AI",
            "GenAI & LLM Integration",
        ],
        "accelerators": ["R-SmartAssist", "R-Optimizer"],
        "technologies": ["llm", "rag", "langchain", "llamaindex", "embeddings", "vector database"],
        "fit_weight": 1.0,
    },
    "manual_workaround": {
        "practices": [
            "Process Automation",
            "Digital Transformation",
            "DevOps & Automation",
        ],
        "accelerators": ["R-SmartAssist", "R-Optimizer"],
        "technologies": [],
        "fit_weight": 0.80,
    },
}


def map_capability(
    pain_category: str,
    technologies: list[str],
) -> CapabilityMatch:
    """
    Map a detected pain category + technologies to internal organizational capabilities.

    Scoring:
    1. Base fit from pain category mapping (0.0–0.5)
    2. Technology overlap bonus (0.0–0.3)
    3. Multi-practice coverage bonus (0.0–0.2)

    Args:
        pain_category: Detected workflow pain category string.
        technologies: Technologies mentioned in the signal.

    Returns:
        CapabilityMatch with practices, accelerators, and strategic fit score.
    """
    registry = CAPABILITY_REGISTRY.get(pain_category)

    if not registry:
        return CapabilityMatch(
            capability_match=False,
            matched_practices=[],
            matched_accelerators=[],
            strategic_fit_score=0.0,
        )

    practices = registry["practices"]
    accelerators = registry["accelerators"]
    base_weight = registry["fit_weight"]
    registry_techs = registry["technologies"]

    # Base category fit (0.0–0.5)
    score = base_weight * 0.5

    # Technology overlap bonus (0.0–0.3)
    if registry_techs and technologies:
        tech_overlap = len(set(t.lower() for t in technologies) & set(registry_techs))
        tech_bonus = min(tech_overlap * 0.1, 0.3)
        score += tech_bonus

    # Multi-practice coverage bonus (0.0–0.2)
    if len(practices) >= 3:
        score += 0.2
    elif len(practices) >= 2:
        score += 0.12

    score = round(min(score, 1.0), 3)

    return CapabilityMatch(
        capability_match=score >= 0.3,
        matched_practices=practices,
        matched_accelerators=accelerators,
        strategic_fit_score=score,
    )
