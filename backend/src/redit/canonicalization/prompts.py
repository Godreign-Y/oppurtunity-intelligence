"""Prompt templates and schema definitions for semantic canonicalization."""

CANONICALIZATION_INSTRUCTION = """
You are an AI semantic normalization engine for market intelligence.

GOAL:
Convert noisy Reddit engineering complaints into CONSISTENT,
BUSINESS-FACING canonical problem intelligence optimized for:
- semantic embeddings
- clustering
- recurring pain aggregation
- business opportunity detection

CRITICAL REQUIREMENTS:

1. SEMANTIC CONSISTENCY IS EXTREMELY IMPORTANT.
2. Similar complaints MUST produce highly similar wording.
3. Reduce semantic spread aggressively.
4. Avoid creative paraphrasing.
5. Prefer deterministic operational phrasing.
6. Preserve important tooling/platform names.
7. Focus on business/operational pain.
8. Return STRICT JSON ONLY.
9. Never explain reasoning.
10. Never generate markdown.

CANONICALIZATION STYLE:

Preferred format:
"<tool/workflow> causing <business impact>"

GOOD:
- "Terraform state management causing deployment delays"
- "Kubernetes ingress configuration causing operational complexity"
- "CI/CD pipeline instability causing release delays"
- "Manual deployment workflows causing engineering inefficiency"

BAD:
- "DevOps nightmare"
- "Infrastructure chaos"
- "Painful tooling experience"
- "Developers struggling with infra"

IMPORTANT:
Prefer SHORT canonical statements.
Do NOT generate long descriptions.

INTENT / PAIN CATEGORY EXAMPLES:
- Infrastructure Orchestration
- DevOps Infrastructure
- Release Engineering
- Workflow Automation
- Operational Visibility
- Security & Compliance
- Deployment Automation
- Infrastructure Scaling
- CI/CD Reliability
- Observability Operations

BUSINESS IMPACT EXAMPLES:
- deployment delays
- engineering productivity loss
- operational inefficiency
- release instability
- infrastructure complexity
- debugging overhead
- operational cost pressure
- workflow disruption

URGENCY VALUES:
- low
- medium
- high

COMPANY INFERENCE RULES:
Infer MAJOR vendor/platform companies associated with the
affected tooling ecosystem.

Examples:
- AWS -> Amazon
- Kubernetes / GKE -> Google
- Azure / GitHub -> Microsoft
- Terraform -> HashiCorp
- Docker -> Docker Inc
- Datadog -> Datadog
- Cloudflare -> Cloudflare

possible_companies_affected should contain:
- ecosystem/platform vendors
- tooling companies
- cloud providers

NOT random unrelated companies.

Return STRICT VALID JSON ONLY.
"""

CANONICALIZATION_FEW_SHOTS = [
    {
        "input": "Terraform state locking ruined our deployments again",
        "output": {
            "problem_statement": "Terraform state management causing deployment delays",
            "pain_category": "Infrastructure Orchestration",
            "affected_tools": ["Terraform"],
            "affected_platforms": [],
            "affected_persona": "DevOps engineers",
            "business_impact": "deployment delays",
            "urgency": "high",
            "solution_category": "Infrastructure orchestration tooling",
            "possible_companies_affected": ["HashiCorp"],
        },
    },
    {
        "input": "Kubernetes ingress config wasted our entire day",
        "output": {
            "problem_statement": "Kubernetes ingress configuration causing operational complexity",
            "pain_category": "DevOps Infrastructure",
            "affected_tools": ["Kubernetes"],
            "affected_platforms": [],
            "affected_persona": "Platform engineers",
            "business_impact": "engineering productivity loss",
            "urgency": "high",
            "solution_category": "Infrastructure orchestration tooling",
            "possible_companies_affected": ["Google"],
        },
    },
    {
        "input": "Our GitHub Actions pipeline keeps failing during releases",
        "output": {
            "problem_statement": "CI/CD pipeline instability causing release delays",
            "pain_category": "Release Engineering",
            "affected_tools": ["GitHub Actions"],
            "affected_platforms": [],
            "affected_persona": "Software engineers",
            "business_impact": "release delays",
            "urgency": "high",
            "solution_category": "Release automation tooling",
            "possible_companies_affected": ["Microsoft"],
        },
    },
    {
        "input": "Datadog alert fatigue is overwhelming our ops team",
        "output": {
            "problem_statement": "Monitoring alert overload causing operational inefficiency",
            "pain_category": "Operational Visibility",
            "affected_tools": ["Datadog"],
            "affected_platforms": [],
            "affected_persona": "Operations teams",
            "business_impact": "operational inefficiency",
            "urgency": "medium",
            "solution_category": "Platform observability tooling",
            "possible_companies_affected": ["Datadog"],
        },
    },
]

CANONICALIZATION_SCHEMA = {
    "type": "object",
    "properties": {
        "problem_statement": {
            "type": "string"
        },
        "pain_category": {
            "type": "string"
        },
        "affected_tools": {
            "type": "array",
            "items": {
                "type": "string"
            },
        },
        "affected_platforms": {
            "type": "array",
            "items": {
                "type": "string"
            },
        },
        "affected_persona": {
            "type": "string"
        },
        "business_impact": {
            "type": "string"
        },
        "urgency": {
            "type": "string"
        },
        "solution_category": {
            "type": "string"
        },
        "possible_companies_affected": {
            "type": "array",
            "items": {
                "type": "string"
            },
        },
        "raw_post_title": {
            "type": "string"
        },
        "raw_post_body": {
            "type": "string"
        },
    },
    "required": [
        "problem_statement",
        "pain_category",
        "affected_tools",
        "affected_platforms",
        "affected_persona",
        "business_impact",
        "urgency",
        "solution_category",
        "possible_companies_affected",
        "raw_post_title",
        "raw_post_body",
    ],
}