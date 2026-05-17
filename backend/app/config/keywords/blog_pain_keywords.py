"""
app/config/keywords/blog_pain_keywords.py

Pain taxonomy for engineering blog signal extraction.

Used by:
- app/utils/normalization.py (detect_pain_indicators_from_text)
- app/services/blog/signal_extractor.py

Maps pain categories (keys) to lists of trigger keywords found in blog content.
To add a new pain type: add a new key with its keyword list.
"""

# Maps a pain type label → list of keywords that indicate that pain in blog posts.
# These pain types are later mapped to the 6 canonical opportunity categories
# via app/config/category_mapper.py.
BLOG_PAIN_TAXONOMY: dict[str, list[str]] = {
    "scaling_pressure": [
        "scaling", "growth", "traffic spike", "load", "capacity", "sharding",
        "distributed", "horizontal scaling", "vertical scaling", "throughput",
        "concurrency", "bottleneck",
    ],
    "deployment_complexity": [
        "deployment", "ci/cd", "pipeline", "release", "rollback",
        "blue-green", "canary", "gitops", "build failure", "hotfix",
        "continuous delivery", "continuous integration",
    ],
    "cloud_cost_pressure": [
        "cost", "spend", "billing", "savings", "optimization", "rightsizing",
        "reserved instances", "spot instances", "cloud bill", "budget",
        "cost overrun", "ec2 cost", "gcp cost",
    ],
    "reliability_issues": [
        "outage", "incident", "downtime", "sla", "slo", "reliability",
        "latency", "p99", "uptime", "mttr", "mttd", "on-call", "pagerduty",
        "alert fatigue",
    ],
    "legacy_modernization": [
        "migration", "rewrite", "refactor", "monolith", "legacy",
        "modernization", "strangler fig", "big bang", "tech debt",
        "technical debt", "decompose", "decomposition",
    ],
    "ai_adoption_uncertainty": [
        "llm", "genai", "generative ai", "ai integration", "ml model",
        "mlops", "vector database", "embeddings", "fine-tuning",
        "prompt engineering", "hallucination", "rag",
    ],
    "security_pressure": [
        "security", "compliance", "soc2", "gdpr", "vulnerability",
        "penetration testing", "zero trust", "iam", "rbac",
        "access control", "data breach", "cve", "patch",
    ],
    "data_pipeline_failure": [
        "data pipeline", "etl", "data quality", "schema drift",
        "data corruption", "stale data", "data freshness",
        "dbt", "airflow", "spark failure", "streaming failure",
    ],
    "observability_gaps": [
        "observability", "tracing", "distributed tracing", "logging",
        "metrics", "grafana", "prometheus", "opentelemetry",
        "no visibility", "debugging", "root cause",
    ],
    "mlops_scaling": [
        "model serving", "inference", "gpu", "model deployment",
        "training pipeline", "feature store", "model registry",
        "a/b testing", "shadow mode", "champion challenger",
    ],
}
