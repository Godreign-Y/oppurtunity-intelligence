"""
app/services/market_pain/schemas.py

Pydantic schemas for the Market Pain Intelligence Pipeline.
Completely separate from the existing Signal schemas — these represent
community-sourced frustration signals, not career/blog signals.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class RedditPost(BaseModel):
    """Raw Reddit post after initial fetch, before any filtering."""

    post_id: str
    subreddit: str
    title: str
    body: str
    author: str = ""
    upvotes: int = 0
    num_comments: int = 0
    url: str = ""
    created_utc: float = 0.0
    permalink: str = ""


class FilteredPost(BaseModel):
    """Post that has survived metadata + relevance filtering."""

    post_id: str
    subreddit: str
    title: str
    body: str
    author: str = ""
    upvotes: int = 0
    num_comments: int = 0
    url: str = ""
    permalink: str = ""
    created_utc: float = 0.0
    tech_relevance_score: float = 0.0
    relevance_label: str = ""


class ExtractedEntities(BaseModel):
    """Entities extracted from a filtered post."""

    products: list[str] = Field(default_factory=list)
    companies: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    workflows: list[str] = Field(default_factory=list)


class FrustrationResult(BaseModel):
    """Output of frustration detection on a post."""

    frustration_detected: bool = False
    sentiment_score: float = 0.0
    frustration_keywords: list[str] = Field(default_factory=list)


class WorkflowPainResult(BaseModel):
    """Output of workflow/enterprise pain detection."""

    workflow_pain_detected: bool = False
    pain_category: str = ""
    pain_subcategories: list[str] = Field(default_factory=list)
    severity: str = "low"  # low | medium | high | critical
    pain_keywords_matched: list[str] = Field(default_factory=list)


class CapabilityMatch(BaseModel):
    """Maps detected pain to internal organizational capability."""

    capability_match: bool = False
    matched_practices: list[str] = Field(default_factory=list)
    matched_accelerators: list[str] = Field(default_factory=list)
    strategic_fit_score: float = 0.0


class MarketPainSignalSchema(BaseModel):
    """
    Unified Market Pain Signal — the final enriched output of the pipeline.
    Each instance represents a validated, scored community frustration signal.
    """

    post_id: str
    source: str = "reddit"
    subreddit: str = ""
    title: str = ""
    body: str = ""
    url: str = ""
    author: str = ""
    upvotes: int = 0
    num_comments: int = 0

    # Extracted entities
    product: Optional[str] = None
    company: Optional[str] = None
    technologies: list[str] = Field(default_factory=list)
    workflows: list[str] = Field(default_factory=list)

    # Pain analysis
    pain_category: str = ""
    opportunity_category: str = ""
    pain_subcategories: list[str] = Field(default_factory=list)
    workflow_pains: list[str] = Field(default_factory=list)
    severity: str = "low"

    # Scores
    tech_confidence: float = 0.0
    sentiment_score: float = 0.0
    business_relevance: float = 0.0
    momentum_score: float = 0.0
    capability_matches: list[str] = Field(default_factory=list)
    strategic_fit_score: float = 0.0
    confidence: float = 0.0  # composite final score

    # Capability mapping
    matched_practices: list[str] = Field(default_factory=list)
    matched_accelerators: list[str] = Field(default_factory=list)

    # Metadata
    timestamp: Optional[str] = None
    created_utc: float = 0.0


class MarketPainSignalResponse(MarketPainSignalSchema):
    """API response schema for a persisted MarketPainSignal record."""

    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
