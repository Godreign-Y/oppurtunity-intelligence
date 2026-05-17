"""Step 9 — semantic workflow/business pain detection."""

import asyncio
from typing import cast

from redit.config.settings import Settings
from redit.filters.base import FilterStage
from redit.ml.registry import ModelRegistry
from redit.ml.workflow_pain import (
    WorkflowPainResult,
    WorkflowPainScorer,
)
from redit.models.pipeline import (
    FilterDecision,
    FilterResult,
    PipelineStageName,
)
from redit.models.reddit import RawRedditPost
from redit.pipelines.context import PipelineContext


class WorkflowPainFilter(FilterStage):
    """Semantic workflow pain detector."""

    def __init__(
        self,
        settings: Settings,
        models: ModelRegistry,
    ) -> None:

        _ = settings

        self._models = models

    @property
    def stage_name(
        self,
    ) -> PipelineStageName:

        return (
            PipelineStageName.WORKFLOW_PAIN
        )

    async def apply(
        self,
        post: RawRedditPost,
        context: PipelineContext,
    ) -> FilterResult:

        _ = context

        scorer = cast(
            WorkflowPainScorer,
            self._models.workflow_pain,
        )

        result = cast(
            WorkflowPainResult,
            await asyncio.to_thread(
                scorer.score,
                post.combined_text,
            ),
        )

        return FilterResult(
            stage=self.stage_name,
            decision=FilterDecision.PASS,
            metadata={
                "workflow_pain_detected":
                    result.detected,
                "business_relevance":
                    round(
                        result.relevance,
                        4,
                    ),
                "workflow_positive_similarity":
                    round(
                        result.positive_similarity,
                        4,
                    ),
                "workflow_negative_similarity":
                    round(
                        result.negative_similarity,
                        4,
                    ),
            },
        )