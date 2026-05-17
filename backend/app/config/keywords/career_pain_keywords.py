"""
app/config/keywords/career_pain_keywords.py

Keyword-to-pain-type mapping for career page signals (job title analysis).

Used by:
- app/services/career/signal_extractor.py

Maps a keyword found in a job title to a canonical pain indicator category.
To add a new mapping: add { "keyword_in_job_title": "pain_type_label" }.
"""

# Maps a keyword found in a job title → internal pain indicator type string.
# These pain types are later mapped to the 6 canonical opportunity categories
# via app/config/category_mapper.py.
CAREER_PAIN_KEYWORD_MAP: dict[str, str] = {
    # Infra & Platform scaling
    "kubernetes": "infra_scaling",
    "k8s": "infra_scaling",
    "platform engineer": "infra_scaling",
    "infrastructure engineer": "infra_scaling",
    "site reliability": "reliability_pressure",
    "sre": "reliability_pressure",
    "distributed systems": "scaling_pressure",

    # Cloud & Automation
    "terraform": "cloud_automation",
    "cloud architect": "cloud_migration",
    "cloud migration": "cloud_migration",
    "cloud engineer": "cloud_migration",
    "aws engineer": "cloud_migration",
    "gcp engineer": "cloud_migration",

    # CI/CD & DevOps
    "ci/cd": "deployment_complexity",
    "cicd": "deployment_complexity",
    "devops": "deployment_complexity",
    "release engineer": "deployment_complexity",
    "build engineer": "deployment_complexity",

    # Observability
    "observability": "monitoring_gaps",
    "monitoring": "monitoring_gaps",

    # AI / ML
    "ai engineer": "ai_initiative",
    "ml engineer": "ai_initiative",
    "machine learning": "ai_initiative",
    "llm": "ai_initiative",
    "mlops": "mlops_scaling",
    "model deployment": "mlops_scaling",
    "data scientist": "ai_initiative",
    "research engineer": "ai_initiative",

    # Security
    "security engineer": "security_pressure",
    "devsecops": "security_pressure",
    "appsec": "security_pressure",

    # Data
    "data engineer": "data_scaling",
    "data platform": "data_scaling",
    "analytics engineer": "data_scaling",

    # Legacy / Modernization
    "modernization": "legacy_modernization",
    "migration": "legacy_modernization",
    "refactor": "legacy_modernization",
}
