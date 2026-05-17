"""Semantic frustration detection filter."""

import asyncio

from redit.filters.base import FilterStage
from redit.ml.registry import ModelRegistry
from redit.models.pipeline import FilterDecision, FilterResult, PipelineStageName
from redit.models.reddit import RawRedditPost
from redit.pipelines.context import PipelineContext


class FrustrationFilter(FilterStage):
    """Reject posts without semantic developer frustration."""

    def __init__(self, models: ModelRegistry) -> None:
        """Inject frustration analyzer."""
        self._models = models

    @property
    def stage_name(self) -> PipelineStageName:
        """Stage identifier."""
        return PipelineStageName.FRUSTRATION

    async def apply(
        self,
        post: RawRedditPost,
        context: PipelineContext,
    ) -> FilterResult:
        """Detect semantic frustration."""
        _ = context

        text = post.combined_text

        analyzer = self._models.frustration

        result = await asyncio.to_thread(
            analyzer.score,
            text,
        )

        if not result.frustration_detected:
            return FilterResult(
                stage=self.stage_name,
                decision=FilterDecision.REJECT,
                reason_code="NOT_FRUSTRATION",
                detail=f"{result.label} ({result.score:.3f})",
                metadata={
                    "frustration_score": result.score,
                    "frustration_label": result.label,
                    "frustration_detected": False,
                },
            )

        return FilterResult(
            stage=self.stage_name,
            decision=FilterDecision.PASS,
            metadata={
                "frustration_score": result.score,
                "frustration_label": result.label,
                "frustration_detected": True,
            },
        )