"""Canonicalization stage to normalize validated Reddit posts into business pain intelligence."""

from redit.canonicalization import canonicalize_post
from redit.filters.base import FilterStage
from redit.models.pipeline import FilterDecision, FilterResult, PipelineStageName
from redit.models.reddit import RawRedditPost
from redit.pipelines.context import PipelineContext


class CanonicalizationFilter(FilterStage):
    """Transform validated posts into canonical business problem metadata."""

    @property
    def stage_name(self) -> PipelineStageName:
        return PipelineStageName.CANONICALIZATION

    async def apply(self, post: RawRedditPost, context: PipelineContext) -> FilterResult:
        canonical_problem = canonicalize_post(post, context.accumulated)
        return FilterResult(
            stage=self.stage_name,
            decision=FilterDecision.PASS,
            metadata=canonical_problem.model_dump(),
        )
