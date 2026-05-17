"""Validated intelligence JSON (Step 10 output)."""

from datetime import datetime

from pydantic import BaseModel, Field

SCHEMA_VERSION = "1.0"


class IntelligenceRecord(BaseModel):
    """
    Structured high-signal post after all pipeline filters pass.

    This is the only artifact persisted for validated posts.
    """

    schema_version: str = Field(default=SCHEMA_VERSION)
    post_id: str
    subreddit: str
    title: str
    body: str
    upvotes: int
    timestamp: datetime
    permalink: str
    product: str | None = None
    company: str | None = None
    tech_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Semantic tech relevance score (0-1).",
    )
    frustration_score: float = Field(
        description="Semantic frustration confidence score (0 to 1).",
    )
    frustration_detected: bool = False
    business_relevance: float = Field(
        ge=0.0,
        le=1.0,
        description="Commercial / workflow pain relevance (0-1).",
    )
    workflow_pain_detected: bool = False
    problem_statement: str = Field(
        default="",
        description="Canonicalized business-facing problem statement.",
    )
    pain_category: str = Field(
        default="",
        description="High-level business pain category.",
    )
    affected_tools: list[str] = Field(
        default_factory=list,
        description="Tools or platforms implicated in the pain.",
    )
    affected_platforms: list[str] = Field(
        default_factory=list,
        description="Affected infrastructure or cloud platforms.",
    )
    affected_persona: str = Field(
        default="",
        description="Primary persona affected by the problem.",
    )
    business_impact: str = Field(
        default="",
        description="Primary business impact of the canonical problem.",
    )
    urgency: str = Field(
        default="",
        description="Relative urgency of the identified pain.",
    )
    solution_category: str = Field(
        default="",
        description="Suggested solution opportunity category.",
    )
    possible_companies_affected: list[str] = Field(
        default_factory=list,
        description="Vendor/platform companies associated with the affected tooling ecosystem.",
    )
    ingestion_run_id: str
    matched_keywords: list[str] = Field(default_factory=list)
