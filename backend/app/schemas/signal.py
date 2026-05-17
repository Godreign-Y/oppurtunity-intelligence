"""
app/schemas/signal.py

Pydantic schemas for signal request/response validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class UnifiedSignalSchema(BaseModel):
    """
    Unified Signal Schema — all sources normalize into this structure.
    Matches the canonical schema defined in the BRD Section 6.
    """

    company_name: str
    source_type: str  # 'career_page' | 'engineering_blog'
    event_type: Optional[str] = None
    technologies: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    pain_indicators: list[str] = Field(default_factory=list)
    business_implications: list[str] = Field(default_factory=list)
    opportunity_mapping: list[str] = Field(default_factory=list)
    opportunity_category: Optional[str] = None
    confidence: float = 0.0
    evidence: list[str] = Field(default_factory=list)
    source_url: Optional[str] = None
    timestamp: Optional[str | datetime] = None

    # Career-specific optional fields
    role_title: Optional[str] = None
    department: Optional[str] = None
    seniority: Optional[str] = None
    location: Optional[str] = None
    urgency: str = "Medium"


class SignalResponse(UnifiedSignalSchema):
    """
    API response schema for a persisted Signal record.
    Extends UnifiedSignalSchema with database fields.
    """

    id: uuid.UUID
    company_id: uuid.UUID
    ai_analysis: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalyzeCompanyRequest(BaseModel):
    """
    Request body for triggering the full company analysis pipeline.
    """

    company_name: str = Field(..., description="Name of the company to analyze")
    pipelines_selected: list[str] = Field(
        default=["career", "blog", "market_pain", "git_issues", "funding", "hiring"],
        description="List of pipelines to run"
    )

class PipelineRunResponse(BaseModel):
    id: uuid.UUID
    company_name: str
    status: str
    pipelines_selected: list[str]
    results: Optional[dict] = None
    errors: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIOpportunityOutput(BaseModel):
    """
    Structured output from the AI inference layer.
    """

    detected_opportunity: str
    confidence: float
    reasoning: list[str]
    recommended_outreach: dict
