"""Future embedding generation for similarity and clustering (placeholder)."""

from redit.filters.base import FilterStage
from redit.models.pipeline import FilterDecision, FilterResult, PipelineStageName
from redit.models.reddit import RawRedditPost


class EmbeddingsFilter(FilterStage):
    """
    Placeholder for vector embedding attachment.

    TODO: Generate embeddings via sentence-transformers or API.
    TODO: Attach vector reference to pipeline context (not persisted in Phase 1).
    """

    @property
    def stage_name(self) -> PipelineStageName:
        """Stage identifier."""
        return PipelineStageName.EMBEDDINGS

    async def apply(self, post: RawRedditPost) -> FilterResult:
        """Pass-through; embeddings do not reject posts."""
        return FilterResult(
            stage=self.stage_name,
            decision=FilterDecision.PASS,
            metadata={"placeholder": True, "embedding": None},
        )
