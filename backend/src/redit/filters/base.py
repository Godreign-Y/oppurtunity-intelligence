"""Base filter stage contract."""

from abc import ABC, abstractmethod

from redit.models.pipeline import FilterResult, PipelineStageName
from redit.models.reddit import RawRedditPost
from redit.pipelines.context import PipelineContext


class FilterStage(ABC):
    """Single stage in the streaming filtration pipeline."""

    @property
    @abstractmethod
    def stage_name(self) -> PipelineStageName:
        """Unique stage identifier."""

    @abstractmethod
    async def apply(self, post: RawRedditPost, context: PipelineContext) -> FilterResult:
        """
        Evaluate one post using accumulated pipeline context.

        Returns FilterResult with PASS or REJECT. Caller stops pipeline on REJECT.
        """
