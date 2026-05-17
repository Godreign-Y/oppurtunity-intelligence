"""Pipeline run and filter result models."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from redit.models.discovery import GlobalFeed
from redit.models.intelligence import IntelligenceRecord
from redit.models.reddit import RawRedditPost, RedditSort


class PipelineStageName(str, Enum):
    """Named pipeline stages (extensible for future ML steps)."""

    METADATA = "metadata"
    TECH_KEYWORDS = "tech_keywords"
    SEMANTIC_CLASSIFIER = "semantic_classifier"
    PRODUCT_EXTRACTION = "product_extraction"
    BUSINESS_VALIDATION = "business_validation"
    FRUSTRATION = "frustration"
    WORKFLOW_PAIN = "workflow_pain"
    CANONICALIZATION = "canonicalization"
    EMBEDDINGS = "embeddings"
    CLUSTERING = "clustering"
    INTELLIGENCE_STORE = "intelligence_store"


class FilterDecision(str, Enum):
    """Outcome of a single filter stage."""

    PASS = "pass"
    REJECT = "reject"


class FilterResult(BaseModel):
    """Result returned by each filter stage."""

    stage: PipelineStageName
    decision: FilterDecision
    reason_code: str | None = None
    detail: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PipelineRejectRecord(BaseModel):
    """Lightweight record when a post is rejected (no full body storage)."""

    reddit_post_id: str
    subreddit: str
    stage: PipelineStageName
    reason_code: str
    detail: str | None = None


class IngestionRunStatus(str, Enum):
    """Lifecycle status of an ingestion run."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class IngestionRequest(BaseModel):
    """Request body for Reddit discovery ingestion."""

    source_mode: str = Field(
        default="subreddits",
        description=(
            "Discovery mode: "
            "feeds | subreddits | search | hybrid"
        ),
    )

    feeds: list[GlobalFeed] | None = Field(
        default_factory=list,
        description="Global feeds like all/popular.",
    )

    subreddits: list[str] | None = Field(
        default_factory=list,
        description="Subreddits to ingest from.",
    )

    search_queries: list[str] | None = Field(
        default_factory=list,
        description="Reddit search queries.",
    )

    limit_per_source: int = Field(
        default=100,
        ge=1,
        le=100000,
        description="Maximum posts to fetch per source.",
    )

    sort: RedditSort = Field(
        default="new",
        description="Listing sort order.",
    )

    dry_run: bool = Field(
        default=False,
        description="Run ingestion without persistence.",
    )


class IngestionResponse(BaseModel):
    """Response after a completed ingestion run."""

    run_id: UUID
    status: IngestionRunStatus
    sources: list[str] = Field(description="Feeds and searches used for this run.")
    posts_fetched: int = 0
    posts_passed: int = 0
    posts_rejected: int = 0
    rejects_by_stage: dict[str, int] = Field(default_factory=dict)
    started_at: datetime
    finished_at: datetime | None = None
    error_message: str | None = None


class IngestionRunSummary(BaseModel):
    """Internal run state persisted during ingestion."""

    run_id: UUID
    status: IngestionRunStatus
    started_at: datetime
    finished_at: datetime | None = None
    sources: list[str] = Field(default_factory=list)
    sort: RedditSort = "hot"
    limit_per_source: int = 50
    posts_fetched: int = 0
    posts_passed: int = 0
    posts_rejected: int = 0
    rejects_by_stage: dict[str, int] = Field(default_factory=dict)
    error_message: str | None = None


class PipelineRunResult(BaseModel):
    """Outcome of processing a single post through the pipeline."""

    post: RawRedditPost
    passed: bool
    rejects: list[PipelineRejectRecord] = Field(default_factory=list)
    stage_results: list[FilterResult] = Field(default_factory=list)
    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    intelligence: IntelligenceRecord | None = Field(
        default=None,
        description="Validated intelligence JSON when post passed all filters.",
    )
