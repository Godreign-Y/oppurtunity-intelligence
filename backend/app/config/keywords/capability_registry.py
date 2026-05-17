"""
app/config/keywords/capability_registry.py

Internal organizational capability registry for the Reddit/F5Bot pipeline.

Used by:
- app/services/market_pain/capability_mapper.py

Maps workflow pain categories → internal service practices + accelerator tools.
This connects community frustrations to the consulting services we can offer.

To add a new capability: add a key matching a WORKFLOW_PAIN_TAXONOMY category,
with "practices", "accelerators", "technologies", and "fit_weight".
"""

# ── Capability Registry ──────────────────────────────────────────────────────
# Maps pain_category → internal organizational capabilities.
# Keys MUST match keys in WORKFLOW_PAIN_TAXONOMY.
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
