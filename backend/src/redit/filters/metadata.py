"""Step 3 — lightweight metadata filtering (quality + freshness only)."""

from datetime import datetime, timedelta, timezone

from redit.config.settings import Settings
from redit.filters.base import FilterStage
from redit.models.pipeline import FilterDecision, FilterResult, PipelineStageName
from redit.models.reddit import RawRedditPost
from redit.pipelines.context import PipelineContext


class MetadataFilter(FilterStage):
    """
    Lightweight metadata gate.

    Purpose:
    - Remove deleted/empty/spam-like posts
    - Keep recall HIGH
    - Let downstream ML filters do the real intelligence filtering

    IMPORTANT:
    We intentionally DO NOT aggressively filter on engagement
    because:
    - fresh posts have low upvotes/comments
    - niche pain points often never go viral
    - intelligence systems need high recall at ingestion
    """

    def __init__(self, settings: Settings) -> None:
        """Load thresholds from settings."""
        self._settings = settings

    @property
    def stage_name(self) -> PipelineStageName:
        """Stage identifier."""
        return PipelineStageName.METADATA

    async def apply(
        self,
        post: RawRedditPost,
        context: PipelineContext,
    ) -> FilterResult:
        """Apply lightweight quality + recency checks."""
        _ = context

        text = post.combined_text.strip().lower()

        # ---------------------------------------------------
        # Remove deleted / removed / empty posts
        # ---------------------------------------------------
        invalid_markers = {
            "",
            "[deleted]",
            "[removed]",
            "deleted",
            "removed",
        }

        if text in invalid_markers:
            return FilterResult(
                stage=self.stage_name,
                decision=FilterDecision.REJECT,
                reason_code="EMPTY_OR_REMOVED",
                detail="post content removed or empty",
            )

        # ---------------------------------------------------
        # Minimal text length filter
        # Keep LOW for high recall
        # ---------------------------------------------------
        if len(text) < self._settings.min_text_length:
            return FilterResult(
                stage=self.stage_name,
                decision=FilterDecision.REJECT,
                reason_code="TOO_SHORT",
                detail=f"text length {len(text)} < {self._settings.min_text_length}",
            )

        # ---------------------------------------------------
        # Optional engagement filter
        # Only reject extremely negative scores
        # DO NOT aggressively filter on upvotes
        # ---------------------------------------------------
        if post.score < -5:
            return FilterResult(
                stage=self.stage_name,
                decision=FilterDecision.REJECT,
                reason_code="HEAVILY_DOWNVOTED",
                detail=f"score {post.score} < -5",
            )

        # ---------------------------------------------------
        # Recency filter
        # Keep relatively fresh data for market intelligence
        # ---------------------------------------------------
        cutoff = datetime.now(timezone.utc) - timedelta(
            days=self._settings.recency_days
        )

        if post.created_at < cutoff:
            return FilterResult(
                stage=self.stage_name,
                decision=FilterDecision.REJECT,
                reason_code="STALE",
                detail=f"post older than {self._settings.recency_days} days",
            )

        # ---------------------------------------------------
        # PASS
        # ---------------------------------------------------
        return FilterResult(
            stage=self.stage_name,
            decision=FilterDecision.PASS,
        )
