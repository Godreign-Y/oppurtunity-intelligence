"""Construct ordered filter pipeline from settings."""

from redit.config.settings import Settings
from redit.filters.base import FilterStage
from redit.filters.metadata import MetadataFilter
from redit.filters.product import (
    BusinessValidationFilter,
    ProductExtractionFilter,
)
from redit.filters.canonicalization import CanonicalizationFilter
from redit.filters.semantic import SemanticClassifierFilter
from redit.filters.frustration import FrustrationFilter
from redit.filters.workflow import WorkflowPainFilter
from redit.ml.registry import ModelRegistry


def build_filter_pipeline(
    settings: Settings,
    models: ModelRegistry,
) -> list[FilterStage]:
    """
    Return ordered filter stages for streaming processing.

    Priority:
    cheap metadata
    → semantic relevance
    → product extraction
    → semantic frustration
    → workflow pain
    → business validation
    """

    return [
    MetadataFilter(
        settings=settings,
    ),

    SemanticClassifierFilter(
        models=models,
    ),

    ProductExtractionFilter(),

    FrustrationFilter(
        models=models,
    ),

    WorkflowPainFilter(
        settings=settings,
        models=models,
    ),

    BusinessValidationFilter(
        settings=settings,
    ),

    CanonicalizationFilter(),
]