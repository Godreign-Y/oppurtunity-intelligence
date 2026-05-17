"""Stream pipeline: process one Reddit post through filter stages."""

from uuid import UUID

from redit.filters.base import FilterStage
from redit.intelligence.builder import IntelligenceBuilder
from redit.models.pipeline import (
    FilterDecision,
    PipelineRejectRecord,
    PipelineRunResult,
)
from redit.models.reddit import RawRedditPost
from redit.pipelines.context import PipelineContext
from redit.utils.logging import get_logger

logger = get_logger(__name__)


class PipelineOrchestrator:
    """
    Pure semantic filtering pipeline.

    Responsibilities:
    - filtering
    - normalization
    - canonicalization
    - intelligence extraction

    NO:
    - embeddings
    - database
    - persistence
    """

    def __init__(
        self,
        stages: list[FilterStage],
        intelligence_builder:
            IntelligenceBuilder | None = None,
    ) -> None:

        self._stages = stages

        self._builder = (
            intelligence_builder
            or IntelligenceBuilder()
        )

    async def process_post(
        self,
        post: RawRedditPost,
        run_id: UUID,
    ) -> PipelineRunResult:
        """
        Process one Reddit post
        through semantic pipeline only.
        """

        context = PipelineContext(
            run_id=run_id
        )

        stage_results = []

        rejects: list[
            PipelineRejectRecord
        ] = []

        for stage in self._stages:

            result = await stage.apply(
                post,
                context,
            )

            stage_results.append(result)

            if (
                result.decision
                == FilterDecision.PASS
            ):

                if result.metadata:

                    context.merge_metadata(
                        result.metadata
                    )

                continue

            reject = (
                PipelineRejectRecord(
                    reddit_post_id=post.id,
                    subreddit=post.subreddit,
                    stage=result.stage,
                    reason_code=(
                        result.reason_code
                        or "UNKNOWN"
                    ),
                    detail=result.detail,
                )
            )

            rejects.append(reject)

            logger.info(
                "Post rejected",
                extra={
                    "post_id": post.id,
                    "stage":
                        result.stage.value,
                    "reason":
                        result.reason_code,
                },
            )

            return PipelineRunResult(
                post=post,
                passed=False,
                rejects=rejects,
                stage_results=stage_results,
                intelligence=None,
            )

        intelligence = self._builder.build(
            post,
            context,
            run_id,
        )

        logger.debug(
            "Post passed semantic pipeline",
            extra={
                "post_id": post.id,
                "product":
                    intelligence.product,
            },
        )

        return PipelineRunResult(
            post=post,
            passed=True,
            rejects=rejects,
            stage_results=stage_results,
            intelligence=intelligence,
        )