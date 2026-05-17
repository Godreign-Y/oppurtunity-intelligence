"""Batch clustering stage placeholder (runs post-ingestion, not per-post reject)."""

from redit.filters.base import FilterStage
from redit.models.pipeline import FilterDecision, FilterResult, PipelineStageName
from redit.models.reddit import RawRedditPost


class ClusteringFilter(FilterStage):
    """
    Placeholder for market-gap clustering across intelligence records.

    TODO: Move to batch job after run completes; group by product + pain theme.
    TODO: Emit market_gap.json — not a per-post rejection stage.
    """

    @property
    def stage_name(self) -> PipelineStageName:
        """Stage identifier."""
        return PipelineStageName.CLUSTERING

    async def apply(self, post: RawRedditPost) -> FilterResult:
        """No-op pass; clustering is batch-oriented."""
        return FilterResult(
            stage=self.stage_name,
            decision=FilterDecision.PASS,
            metadata={"placeholder": True, "note": "batch stage only"},
        )
