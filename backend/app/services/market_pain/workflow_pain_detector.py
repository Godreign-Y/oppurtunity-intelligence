"""
app/services/market_pain/workflow_pain_detector.py

Phase 5b — THE MOST IMPORTANT MODULE.
Detects enterprise workflow pain, operational blockers, scaling failures,
and production reliability gaps. Goes far deeper than generic negativity.

Differentiates:
  Weak: "This UI sucks"
  Strong: "Our enterprise deployment fails because permission handling is broken"
"""

import logging

from app.services.market_pain.schemas import FilteredPost, WorkflowPainResult

logger = logging.getLogger(__name__)

# Pain category taxonomy with keyword patterns
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

# Severity amplifiers — phrases that indicate critical business impact
SEVERITY_AMPLIFIERS: list[str] = [
    "our company", "our team", "our org", "our enterprise",
    "in production", "in prod", "production environment",
    "critical", "urgent", "emergency", "p0", "p1", "sev1", "sev0",
    "blocking", "blocker", "showstopper", "deal breaker",
    "losing customers", "lost revenue", "cost us", "costing us",
    "compliance deadline", "audit", "regulation",
    "whole team", "entire team", "everyone on the team",
]


def detect_workflow_pain(post: FilteredPost) -> WorkflowPainResult:
    """
    Detect enterprise workflow pain, operational blockers, and production issues.

    Scoring logic:
    1. Match against WORKFLOW_PAIN_TAXONOMY categories
    2. Pick the highest-weight matched category as primary
    3. Compute severity based on keyword density + amplifiers
    4. Return structured pain assessment

    Args:
        post: Relevance-filtered post.

    Returns:
        WorkflowPainResult with category, severity, and matched keywords.
    """
    combined = f"{post.title} {post.body}".lower()

    category_scores: dict[str, tuple[int, float, list[str]]] = {}

    for category, config in WORKFLOW_PAIN_TAXONOMY.items():
        keywords = config["keywords"]
        weight = config["weight"]
        matched = [kw for kw in keywords if kw in combined]

        if matched:
            category_scores[category] = (len(matched), weight, matched)

    if not category_scores:
        return WorkflowPainResult(
            workflow_pain_detected=False,
            pain_category="",
            pain_subcategories=[],
            severity="low",
            pain_keywords_matched=[],
        )

    # Primary category = highest (match_count * weight)
    primary = max(
        category_scores.items(),
        key=lambda x: x[1][0] * x[1][1],
    )
    primary_category = primary[0]
    primary_matches = primary[1][2]

    # Collect all matched subcategories
    subcategories = [cat for cat in category_scores if cat != primary_category]

    # All matched keywords across categories
    all_keywords: list[str] = []
    for _, (_, _, matched) in category_scores.items():
        all_keywords.extend(matched)

    # Compute severity
    amplifier_count = sum(1 for amp in SEVERITY_AMPLIFIERS if amp in combined)
    total_pain_matches = sum(count for count, _, _ in category_scores.values())

    if amplifier_count >= 3 or total_pain_matches >= 6:
        severity = "critical"
    elif amplifier_count >= 2 or total_pain_matches >= 4:
        severity = "high"
    elif amplifier_count >= 1 or total_pain_matches >= 2:
        severity = "medium"
    else:
        severity = "low"

    return WorkflowPainResult(
        workflow_pain_detected=True,
        pain_category=primary_category,
        pain_subcategories=subcategories,
        severity=severity,
        pain_keywords_matched=list(set(all_keywords))[:15],
    )
