"""
app/config/category_mapper.py

THE SINGLE SOURCE OF TRUTH for mapping any internal pain/signal type
to one of the 6 canonical opportunity categories.

All pipelines (career, blog, reddit, github, hiring, funding) MUST call
`map_to_opportunity_category()` before persisting a signal.

The 6 canonical categories are:
  - AI Infrastructure
  - Cloud Migration
  - DevOps Modernization
  - MLOps Scaling
  - Legacy Refactoring
  - Cost Optimization
"""

from app.config.keywords.opportunity_categories import OpportunityCategory

# ── Master Pain → Category Mapping ──────────────────────────────────────────
# Maps every internal pain type (from career, blog, reddit, github, hiring)
# to one of the 6 canonical opportunity categories.
#
# Internal pain types come from:
#   - CAREER_PAIN_KEYWORD_MAP values (career pipeline)
#   - BLOG_PAIN_TAXONOMY keys (blog pipeline)
#   - WORKFLOW_PAIN_TAXONOMY keys (reddit/f5bot pipeline)
#   - GitHub issue analysis labels
#   - Funding classifier labels
#   - Hiring signal labels
_PAIN_TO_CATEGORY: dict[str, str] = {
    # ── Career / Blog Pain Types ────────────────────────────────────────────
    "infra_scaling": OpportunityCategory.CLOUD_MIGRATION,
    "cloud_automation": OpportunityCategory.CLOUD_MIGRATION,
    "cloud_migration": OpportunityCategory.CLOUD_MIGRATION,
    "scaling_pressure": OpportunityCategory.DEVOPS_MODERNIZATION,
    "reliability_pressure": OpportunityCategory.DEVOPS_MODERNIZATION,
    "deployment_complexity": OpportunityCategory.DEVOPS_MODERNIZATION,
    "monitoring_gaps": OpportunityCategory.DEVOPS_MODERNIZATION,
    "observability_gaps": OpportunityCategory.DEVOPS_MODERNIZATION,
    "ai_initiative": OpportunityCategory.AI_INFRASTRUCTURE,
    "mlops_scaling": OpportunityCategory.MLOPS_SCALING,
    "security_pressure": OpportunityCategory.DEVOPS_MODERNIZATION,
    "cloud_cost_pressure": OpportunityCategory.COST_OPTIMIZATION,
    "reliability_issues": OpportunityCategory.DEVOPS_MODERNIZATION,
    "legacy_modernization": OpportunityCategory.LEGACY_REFACTORING,
    "ai_adoption_uncertainty": OpportunityCategory.AI_INFRASTRUCTURE,
    "data_scaling": OpportunityCategory.MLOPS_SCALING,
    "data_pipeline_failure": OpportunityCategory.MLOPS_SCALING,

    # ── Workflow Pain Types (Reddit/F5Bot) ──────────────────────────────────
    "enterprise_reliability": OpportunityCategory.DEVOPS_MODERNIZATION,
    "scaling_bottleneck": OpportunityCategory.CLOUD_MIGRATION,
    "deployment_failure": OpportunityCategory.DEVOPS_MODERNIZATION,
    "migration_pain": OpportunityCategory.LEGACY_REFACTORING,
    "security_compliance_gap": OpportunityCategory.DEVOPS_MODERNIZATION,
    "observability_blindness": OpportunityCategory.DEVOPS_MODERNIZATION,
    "integration_friction": OpportunityCategory.LEGACY_REFACTORING,
    "ai_ml_production_pain": OpportunityCategory.AI_INFRASTRUCTURE,
    "manual_workaround": OpportunityCategory.DEVOPS_MODERNIZATION,

    # ── GitHub Issue Labels ─────────────────────────────────────────────────
    "performance": OpportunityCategory.DEVOPS_MODERNIZATION,
    "bug": OpportunityCategory.DEVOPS_MODERNIZATION,
    "infrastructure": OpportunityCategory.CLOUD_MIGRATION,
    "security": OpportunityCategory.DEVOPS_MODERNIZATION,
    "ai": OpportunityCategory.AI_INFRASTRUCTURE,
    "ml": OpportunityCategory.MLOPS_SCALING,
    "cost": OpportunityCategory.COST_OPTIMIZATION,
    "legacy": OpportunityCategory.LEGACY_REFACTORING,
    "migration": OpportunityCategory.LEGACY_REFACTORING,
    "modernization": OpportunityCategory.LEGACY_REFACTORING,
    "devops": OpportunityCategory.DEVOPS_MODERNIZATION,
    "ci/cd": OpportunityCategory.DEVOPS_MODERNIZATION,
    "scaling": OpportunityCategory.CLOUD_MIGRATION,
    "cloud": OpportunityCategory.CLOUD_MIGRATION,

    # ── Funding Signal Labels ───────────────────────────────────────────────
    "series_a": OpportunityCategory.CLOUD_MIGRATION,
    "series_b": OpportunityCategory.DEVOPS_MODERNIZATION,
    "series_c": OpportunityCategory.AI_INFRASTRUCTURE,
    "growth_stage": OpportunityCategory.CLOUD_MIGRATION,
    "ai_startup": OpportunityCategory.AI_INFRASTRUCTURE,
    "saas": OpportunityCategory.DEVOPS_MODERNIZATION,
}


def map_to_opportunity_category(pain_type_or_label: str) -> str:
    """
    Map any internal pain type or signal label to one of the 6 canonical
    opportunity categories.

    Args:
        pain_type_or_label: An internal pain type string from any pipeline.
            E.g. "infra_scaling", "migration_pain", "ai_ml_production_pain"

    Returns:
        A canonical OpportunityCategory string value.
        Defaults to OpportunityCategory.DEVOPS_MODERNIZATION if no mapping found.
    """
    normalized = pain_type_or_label.lower().strip().replace(" ", "_")
    category = _PAIN_TO_CATEGORY.get(normalized, OpportunityCategory.DEVOPS_MODERNIZATION)
    return category.value if isinstance(category, OpportunityCategory) else category


def map_pain_list_to_category(pain_indicators: list[str]) -> str:
    """
    Map a list of pain indicators to the single best opportunity category.

    Takes the first matching pain indicator that has a known mapping.
    Falls back to DEVOPS_MODERNIZATION if none match.

    Args:
        pain_indicators: List of pain type strings from any pipeline.

    Returns:
        A canonical OpportunityCategory string value.
    """
    for pain in pain_indicators:
        category = map_to_opportunity_category(pain)
        if category != OpportunityCategory.DEVOPS_MODERNIZATION.value:
            return category
        # Even DEVOPS_MODERNIZATION is valid — return it if explicitly mapped
        normalized = pain.lower().strip().replace(" ", "_")
        if normalized in _PAIN_TO_CATEGORY:
            return category

    return OpportunityCategory.DEVOPS_MODERNIZATION.value
