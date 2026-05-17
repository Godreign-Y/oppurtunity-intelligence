"""
app/config/keywords/reddit_relevance_keywords.py

Keyword registries used by the Reddit/F5Bot relevance classifier.

Used by:
- app/services/market_pain/relevance_classifier.py

Two-layer keyword system:
1. REDDIT_TECH_KEYWORDS: cheap pre-filter to keep only tech-related posts
2. REDDIT_DOMAIN_CLASSIFIERS: domain classification patterns for semantic scoring
"""

# ── Layer 1: Cheap tech pre-filter ──────────────────────────────────────────
# A post must match at least one of these to pass the relevance filter.
# Used for quick rejection of obviously non-tech content.
REDDIT_TECH_KEYWORDS: list[str] = [
    "ai", "api", "platform", "workflow", "enterprise", "cloud", "saas",
    "llm", "rag", "deployment", "security", "infrastructure", "automation",
    "kubernetes", "docker", "terraform", "microservice", "pipeline",
    "database", "server", "backend", "frontend", "devops", "mlops",
    "integration", "sdk", "oauth", "authentication", "monitoring",
    "observability", "latency", "scaling", "migration", "compliance",
    "data lake", "data warehouse", "etl", "streaming", "kafka",
    "redis", "postgresql", "mongodb", "elasticsearch", "grafana",
    "prometheus", "datadog", "aws", "gcp", "azure", "snowflake",
    "model", "fine-tune", "embedding", "vector", "agent", "chatbot",
    "tool", "plugin", "extension", "software", "app", "service",
]

# ── Layer 2: Semantic domain classifiers ────────────────────────────────────
# Each key is a domain label; each value is a list of keyword patterns.
# Posts are scored against all domains; the highest-scoring domain wins.
# Minimum semantic confidence threshold is applied after scoring.
REDDIT_DOMAIN_CLASSIFIERS: dict[str, list[str]] = {
    "enterprise_tech_discussion": [
        "enterprise", "production", "our company", "our team", "our org",
        "at work", "in production", "deploy", "scale", "compliance",
        "soc2", "gdpr", "hipaa", "vendor", "contract", "license",
        "procurement", "stakeholder", "migration", "legacy",
    ],
    "workflow_pain_discussion": [
        "workflow", "workaround", "manually", "broken", "failing",
        "doesn't work", "can't use", "blocking", "blocker", "pain",
        "frustrating", "unreliable", "inconsistent", "downtime",
        "outage", "incident", "rollback", "hotfix", "hack",
    ],
    "scaling_operational_discussion": [
        "scaling", "performance", "latency", "throughput", "bottleneck",
        "capacity", "load", "traffic", "concurrency", "resource",
        "memory leak", "cpu", "gpu", "costs", "billing", "optimize",
        "horizontal", "vertical", "sharding", "replication",
    ],
    "product_frustration": [
        "switched to", "moved away", "dropped", "cancelled", "refund",
        "support ticket", "bug", "regression", "breaking change",
        "deprecated", "removed feature", "worse", "downgrade",
        "rate limit", "quota", "pricing", "expensive",
    ],
}

# Minimum values for relevance filtering
REDDIT_MIN_TECH_KEYWORD_MATCHES: int = 1
REDDIT_MIN_SEMANTIC_CONFIDENCE: float = 0.5
