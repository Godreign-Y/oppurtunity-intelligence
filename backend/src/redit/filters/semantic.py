"""Step 5 — semantic tech relevance via sentence embeddings."""

import asyncio

from redit.filters.base import FilterStage
from redit.ml.registry import ModelRegistry
from redit.models.pipeline import FilterDecision, FilterResult, PipelineStageName
from redit.models.reddit import RawRedditPost
from redit.pipelines.context import PipelineContext


class SemanticClassifierFilter(FilterStage):
    """Reject posts that are not semantically tech/product discussions."""

    def __init__(self, models: ModelRegistry) -> None:
        """Inject loaded model registry."""
        self._models = models

    @property
    def stage_name(self) -> PipelineStageName:
        """Stage identifier."""
        return PipelineStageName.SEMANTIC_CLASSIFIER

    async def apply(self, post: RawRedditPost, context: PipelineContext) -> FilterResult:
        """Score tech relevance in a worker thread to avoid blocking the event loop."""
        _ = context
        text = post.combined_text
        scorer = self._models.tech_scorer
        result = await asyncio.to_thread(scorer.score, text)

        if not result.is_relevant:
            return FilterResult(
                stage=self.stage_name,
                decision=FilterDecision.REJECT,
                reason_code="LOW_TECH_CONFIDENCE",
                detail=(
                    f"tech_sim={result.tech_similarity:.3f} "
                    f"margin={result.margin:.3f}"
                ),
                metadata={
                    "tech_similarity": result.tech_similarity,
                    "non_tech_similarity": result.non_tech_similarity,
                    "margin": result.margin,
                },
            )

        return FilterResult(
            stage=self.stage_name,
            decision=FilterDecision.PASS,
            metadata={
                "tech_confidence": result.tech_similarity,
                "tech_similarity": result.tech_similarity,
                "non_tech_similarity": result.non_tech_similarity,
                "margin": result.margin,
            },
        )
