"""
app/config/keywords/workflow_pain_taxonomy.py

Workflow pain category taxonomy and severity amplifiers for the Reddit/F5Bot pipeline.

Used by:
- app/services/market_pain/workflow_pain_detector.py

WORKFLOW_PAIN_TAXONOMY: Maps pain categories → keyword patterns + scoring weights.
SEVERITY_AMPLIFIERS: Phrases indicating business-critical impact (escalates severity).

To add a new pain category:
  1. Add a new key to WORKFLOW_PAIN_TAXONOMY with "keywords" list and "weight" float (0.0–1.0).
  2. Add a mapping for it in app/config/category_mapper.py.
"""

# ── Workflow Pain Category Taxonomy ─────────────────────────────────────────
# Each category key maps to a dict with:
#   - "keywords": list[str] — trigger phrases to match in post text
#   - "weight": float — category relevance weight (higher = more important pain)
WORKFLOW_PAIN_TAXONOMY: dict[str, dict] = {
    "enterprise_reliability": {
        "keywords": [
            "outage", "downtime", "incident", "sla breach", "slo",
            "availability", "reliability", "uptime", "failover",
            "disaster recovery", "data loss", "corruption",
            "production issue", "prod issue", "critical failure",
            "service degradation", "partial outage",
        ],
        "weight": 1.0,
    },
    "scaling_bottleneck": {
        "keywords": [
            "scaling", "bottleneck", "throughput", "capacity",
            "load", "traffic spike", "performance degradation",
            "memory leak", "cpu spike", "resource exhaustion",
            "connection pool", "thread starvation", "queue backlog",
            "horizontal scaling", "vertical scaling", "sharding",
            "rate limit", "throttled", "quota exceeded",
        ],
        "weight": 0.95,
    },
    "deployment_failure": {
        "keywords": [
            "deployment fail", "deploy broke", "rollback",
            "broken deployment", "ci/cd failure", "pipeline failed",
            "build failure", "release blocked", "hotfix",
            "canary failed", "blue-green failure", "config drift",
            "environment mismatch", "staging broken",
        ],
        "weight": 0.90,
    },
    "migration_pain": {
        "keywords": [
            "migration", "migrating", "rewrite", "refactor",
            "monolith", "legacy system", "tech debt", "technical debt",
            "strangler fig", "big bang migration", "data migration",
            "cloud migration", "lift and shift", "re-platform",
            "version upgrade", "breaking change", "backward compat",
        ],
        "weight": 0.90,
    },
    "security_compliance_gap": {
        "keywords": [
            "security vulnerability", "data breach", "compliance",
            "soc2", "gdpr", "hipaa", "pci dss", "iso 27001",
            "penetration test", "vulnerability scan", "zero trust",
            "access control", "iam", "rbac", "permission denied",
            "unauthorized access", "audit finding", "audit fail",
        ],
        "weight": 0.95,
    },
    "observability_blindness": {
        "keywords": [
            "no visibility", "blind spot", "can't debug",
            "logging missing", "no logs", "no metrics",
            "monitoring gap", "alerting failure", "false alert",
            "alert fatigue", "mttr", "mttd", "root cause",
            "tracing", "distributed tracing", "observability",
        ],
        "weight": 0.85,
    },
    "integration_friction": {
        "keywords": [
            "api broken", "api changed", "api versioning",
            "integration failure", "webhook failed", "callback fail",
            "sdk broken", "sdk outdated", "incompatible",
            "interoperability", "data sync", "sync failure",
            "connector broken", "plugin broken", "extension fail",
        ],
        "weight": 0.85,
    },
    "data_pipeline_failure": {
        "keywords": [
            "data pipeline", "etl failure", "data loss",
            "data quality", "schema drift", "data corruption",
            "stale data", "data freshness", "batch job failed",
            "streaming failure", "data lake", "data warehouse",
            "dbt failure", "airflow dag", "spark job failed",
        ],
        "weight": 0.90,
    },
    "ai_ml_production_pain": {
        "keywords": [
            "hallucination", "hallucinate", "model accuracy",
            "model drift", "fine-tuning fail", "training failure",
            "inference latency", "token limit", "context window",
            "rag failure", "retrieval failure", "embedding",
            "prompt injection", "guardrail", "safety filter",
            "model serving", "gpu shortage", "cost explosion",
        ],
        "weight": 1.0,
    },
    "manual_workaround": {
        "keywords": [
            "manually", "manual process", "workaround",
            "have to manually", "copy paste", "spreadsheet",
            "by hand", "tedious", "repetitive", "toil",
            "manual step", "human in the loop", "no automation",
            "can't automate", "script broke",
        ],
        "weight": 0.80,
    },
}

# ── Severity Amplifiers ──────────────────────────────────────────────────────
# Phrases that escalate the severity score of a signal.
# More amplifier matches = higher severity level.
SEVERITY_AMPLIFIERS: list[str] = [
    "our company", "our team", "our org", "our enterprise",
    "in production", "in prod", "production environment",
    "critical", "urgent", "emergency", "p0", "p1", "sev1", "sev0",
    "blocking", "blocker", "showstopper", "deal breaker",
    "losing customers", "lost revenue", "cost us", "costing us",
    "compliance deadline", "audit", "regulation",
    "whole team", "entire team", "everyone on the team",
]
