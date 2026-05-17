"""
app/models/market_pain.py

ORM model for Market Pain Intelligence signals.
Completely separate from the existing Signal model — no overloading.
"""

from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base


class MarketPainSignal(Base):
    """
    Represents a validated market pain intelligence signal sourced from
    community platforms (Reddit, HackerNews, GitHub Issues).

    This is independent from the career/blog Signal model.
    """

    __tablename__ = "market_pain_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )

    # Source metadata
    source = Column(String(50), default="reddit")
    post_id = Column(String(100), nullable=False)
    subreddit = Column(String(100), nullable=True)
    title = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    upvotes = Column(Integer, default=0)
    num_comments = Column(Integer, default=0)

    # Extracted entities
    product = Column(String(255), nullable=True)
    company_name_detected = Column(String(255), nullable=True)
    technologies = Column(JSON, default=list)
    workflows = Column(JSON, default=list)

    # Pain analysis
    pain_category = Column(String(100), nullable=True)
    pain_subcategories = Column(JSON, default=list)
    workflow_pains = Column(JSON, default=list)
    severity = Column(String(50), default="low")

    # Scores
    tech_confidence = Column(Float, default=0.0)
    sentiment_score = Column(Float, default=0.0)
    business_relevance = Column(Float, default=0.0)
    momentum_score = Column(Float, default=0.0)
    strategic_fit_score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)

    # Capability mapping
    capability_matches = Column(JSON, default=list)
    matched_practices = Column(JSON, default=list)
    matched_accelerators = Column(JSON, default=list)

    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="market_pain_signals")
