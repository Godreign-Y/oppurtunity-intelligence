"""
app/config/keywords/opportunity_categories.py

THE SINGLE SOURCE OF TRUTH for the 6 canonical opportunity categories.

Every signal from EVERY source (careers, blogs, reddit, github, hiring, funding)
MUST be mapped to exactly one of these categories before being stored or displayed.

These categories represent the consulting service lines we can offer.
"""

from enum import Enum
from typing import FrozenSet


class OpportunityCategory(str, Enum):
    """
    The 6 canonical opportunity categories that all intelligence signals map to.

    Every source pipeline must classify its signals into one of these.
    """

    AI_INFRASTRUCTURE = "AI Infrastructure"
    CLOUD_MIGRATION = "Cloud Migration"
    DEVOPS_MODERNIZATION = "DevOps Modernization"
    MLOPS_SCALING = "MLOps Scaling"
    LEGACY_REFACTORING = "Legacy Refactoring"
    COST_OPTIMIZATION = "Cost Optimization"


# Flat list for validation, display, and DB enum constraints
ALL_OPPORTUNITY_CATEGORIES: list[str] = [cat.value for cat in OpportunityCategory]

# Frozenset for fast membership checks
VALID_CATEGORY_SET: FrozenSet[str] = frozenset(ALL_OPPORTUNITY_CATEGORIES)
