"""
Legacy tech keyword pre-filter.

Disabled in current semantic pipeline.
Retained only for backwards compatibility.
"""

from redit.config.settings import Settings
from redit.filters.base import FilterStage
from redit.models.pipeline import (
    FilterDecision,
    FilterResult,
    PipelineStageName,
)
from redit.models.reddit import RawRedditPost
from redit.pipelines.context import PipelineContext


class TechKeywordsFilter(FilterStage):
    """
    Deprecated keyword filter.

    Current pipeline relies on:
    - semantic workflow pain detection
    - canonicalization
    - embeddings
    - clustering

    This stage now acts as a no-op pass-through.
    """

    def __init__(
        self,
        settings: Settings,
    ) -> None:
        _ = settings

    @property
    def stage_name(
        self,
    ) -> PipelineStageName:

        return (
            PipelineStageName.TECH_KEYWORDS
        )

    async def apply(
        self,
        post: RawRedditPost,
        context: PipelineContext,
    ) -> FilterResult:

        _ = post
        _ = context

        return FilterResult(
            stage=self.stage_name,
            decision=FilterDecision.PASS,
            metadata={
                "legacy_filter_disabled": True
            },
        )