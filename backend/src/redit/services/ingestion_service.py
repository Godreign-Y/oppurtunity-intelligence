"""Global Reddit discovery ingestion and pipeline execution."""

from datetime import datetime, timezone
from uuid import uuid4

from redit.aggregation.orchestrator import AggregationOrchestrator
from redit.config.settings import Settings
from redit.filters.registry import build_filter_pipeline
from redit.ingestion.base import RedditSource
from redit.ingestion.discovery_stream import iter_discovery_posts
from redit.ingestion.factory import create_reddit_source
from redit.ml.registry import ModelRegistry
from redit.models.discovery import GlobalFeed
from redit.models.pipeline import (
    IngestionRequest,
    IngestionResponse,
    IngestionRunStatus,
    IngestionRunSummary,
    PipelineRejectRecord,
)
from redit.pipelines.orchestrator import PipelineOrchestrator
from redit.storage.base import RunStore
from redit.storage.database import AsyncSessionLocal
from redit.utils.logging import get_logger

logger = get_logger(__name__)


class IngestionService:
    """
    Fetches Reddit discovery feeds, subreddit streams,
    and search queries, processes posts one-by-one,
    and stores validated intelligence JSON.
    """

    def __init__(
        self,
        settings: Settings,
        run_store: RunStore,
        models: ModelRegistry,
    ) -> None:
        """Wire settings, storage, and ML models."""

        self._settings = settings
        self._run_store = run_store
        self._models = models

    async def ingest(
        self,
        request: IngestionRequest,
    ) -> IngestionResponse:
        """Run Reddit discovery ingestion and return run summary."""

        run_id = uuid4()

        # ---------------------------------------------------
        # Parse request inputs
        # ---------------------------------------------------

        feeds = request.feeds or []

        subreddits = getattr(
            request,
            "subreddits",
            [],
        ) or []

        searches = request.search_queries or []

        # ---------------------------------------------------
        # Human-readable source tracking
        # ---------------------------------------------------

        sources = (
            [f"r/{feed}" for feed in feeds]
            + [
                f"subreddit:{subreddit}"
                for subreddit in subreddits
            ]
            + [
                f"search:{query}"
                for query in searches
            ]
        )

        # ---------------------------------------------------
        # Create run summary
        # ---------------------------------------------------

        summary = IngestionRunSummary(
            run_id=run_id,
            status=IngestionRunStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
            sources=sources,
            sort=request.sort,
            limit_per_source=request.limit_per_source,
        )

        await self._run_store.create_run(summary)

        source: RedditSource | None = None
        db_session = None

        try:
            # ---------------------------------------------------
            # Create SINGLE database session
            # for full ingestion lifecycle
            # ---------------------------------------------------

            db_session = AsyncSessionLocal()

            # ---------------------------------------------------
            # Create Reddit source
            # ---------------------------------------------------

            source = create_reddit_source(
                self._settings
            )

            # ---------------------------------------------------
            # Build pipeline
            # ---------------------------------------------------

            pipeline = PipelineOrchestrator(
                build_filter_pipeline(
                    self._settings,
                    self._models,
                )
            )

            # ---------------------------------------------------
            # Execute ingestion run
            # ---------------------------------------------------

            summary = await self._execute_run(
                summary=summary,
                source=source,
                pipeline=pipeline,
                feeds=feeds,
                subreddits=subreddits,
                search_queries=searches,
                db_session=db_session,
            )

        except Exception as exc:

            logger.exception(
                "Ingestion run failed",
                extra={"run_id": str(run_id)},
            )

            summary.status = (
                IngestionRunStatus.FAILED
            )

            summary.error_message = str(exc)

            summary.finished_at = datetime.now(
                timezone.utc
            )

            await self._run_store.update_run(
                summary
            )

            # ---------------------------------------------------
            # Rollback full transaction batch
            # ---------------------------------------------------

            if db_session is not None:

                await db_session.rollback()

                logger.info(
                    "Transaction rolled back"
                )

            raise

        finally:

            if source is not None:
                await source.close()

            # ---------------------------------------------------
            # Always close session
            # ---------------------------------------------------

            if db_session is not None:
                await db_session.close()

        return self._to_response(summary)

    async def _execute_run(
        self,
        summary: IngestionRunSummary,
        source: RedditSource,
        pipeline: PipelineOrchestrator,
        feeds: list[GlobalFeed],
        subreddits: list[str],
        search_queries: list[str],
        db_session,
    ) -> IngestionRunSummary:
        """
        Stream Reddit posts and process each
        through the pipeline.

        Uses:
        - ONE session
        - MANY flushes
        - ONE final commit
        """

        rejects_by_stage: dict[str, int] = {}

        async for post in iter_discovery_posts(
            source=source,
            feeds=feeds,
            subreddits=subreddits,
            search_queries=search_queries,
            sort=summary.sort,
            limit_per_source=summary.limit_per_source,
            delay_seconds=(
                self._settings
                .reddit_request_delay_seconds
            ),
        ):

            summary.posts_fetched += 1

            result = await pipeline.process_post(
                post,
                summary.run_id,
                db_session,
            )

            # ---------------------------------------------------
            # Passed intelligence
            # ---------------------------------------------------

            if (
                result.passed
                and result.intelligence
                is not None
            ):

                summary.posts_passed += 1

                await self._run_store.append_intelligence(
                    summary.run_id,
                    result.intelligence,
                )

            # ---------------------------------------------------
            # Rejected
            # ---------------------------------------------------

            else:

                summary.posts_rejected += 1

                self._tally_rejects(
                    rejects_by_stage,
                    result.rejects,
                )

        # ---------------------------------------------------
        # Finalize summary
        # ---------------------------------------------------

        summary.rejects_by_stage = (
            rejects_by_stage
        )

        summary.status = (
            IngestionRunStatus.COMPLETED
        )

        summary.finished_at = datetime.now(
            timezone.utc
        )

        await self._run_store.update_run(
            summary
        )

        logger.info(
            "Ingestion completed",
            extra={
                "run_id": str(summary.run_id),
                "fetched": summary.posts_fetched,
                "passed": summary.posts_passed,
                "rejected": summary.posts_rejected,
            },
        )

        # ---------------------------------------------------
        # Run aggregation pipeline
        # ---------------------------------------------------

        if summary.posts_passed > 0:

            logger.info(
                "Starting aggregation pipeline",
                extra={
                    "records":
                    summary.posts_passed
                },
            )

            aggregation_orchestrator = (
                AggregationOrchestrator()
            )

            aggregation_result = (
                await aggregation_orchestrator.run(
                    db_session
                )
            )

            logger.info(
                "Aggregation completed",
                extra=aggregation_result,
            )

        else:

            logger.info(
                "No records passed; "
                "skipping aggregation"
            )

        # ---------------------------------------------------
        # FINAL SINGLE COMMIT
        # ---------------------------------------------------

        logger.info(
            "Committing full ingestion batch"
        )

        await db_session.commit()

        logger.info(
            "Transaction committed successfully"
        )

        return summary

    def _tally_rejects(
        self,
        rejects_by_stage: dict[str, int],
        rejects: list[PipelineRejectRecord],
    ) -> None:
        """Increment per-stage reject counters."""

        for reject in rejects:

            key = reject.stage.value

            rejects_by_stage[key] = (
                rejects_by_stage.get(key, 0)
                + 1
            )

    def _to_response(
        self,
        summary: IngestionRunSummary,
    ) -> IngestionResponse:
        """Map internal summary to API response."""

        return IngestionResponse(
            run_id=summary.run_id,
            status=summary.status,
            sources=summary.sources,
            posts_fetched=summary.posts_fetched,
            posts_passed=summary.posts_passed,
            posts_rejected=summary.posts_rejected,
            rejects_by_stage=(
                summary.rejects_by_stage
            ),
            started_at=summary.started_at,
            finished_at=summary.finished_at,
            error_message=summary.error_message,
        )