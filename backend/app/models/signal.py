"""
app/models/signal.py

ORM model representing a normalized intelligence signal extracted from
a career page or engineering blog.
"""

from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base


class Signal(Base):
    """
    Represents a normalized intelligence signal from any source.

    Follows the Unified Signal Schema defined in the BRD.

    Attributes:
        id: UUID primary key.
        company_id: FK to the Company table.
        source_type: 'career_page' or 'engineering_blog'.
        event_type: e.g. 'hiring_signal', 'infra_modernization'.
        technologies: JSON list of detected technologies.
        topics: JSON list of detected topics.
        pain_indicators: JSON list of pain categories.
        business_implications: JSON list of business implication strings.
        opportunity_mapping: JSON list of suggested opportunity types.
        confidence: Float confidence score 0.0–1.0.
        evidence: JSON list of evidence strings.
        source_url: URL of the source page.
        ai_analysis: Full AI inference JSON output.
        timestamp: When the signal was captured.
    """

    __tablename__ = "signals"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    source_type: str = Column(String(50), nullable=False)
    event_type: str = Column(String(100), nullable=True)
    technologies: list = Column(JSON, default=list)
    topics: list = Column(JSON, default=list)
    pain_indicators: list = Column(JSON, default=list)
    business_implications: list = Column(JSON, default=list)
    opportunity_mapping: list = Column(JSON, default=list)
    confidence: float = Column(Float, default=0.0)
    evidence: list = Column(JSON, default=list)
    source_url: str = Column(Text, nullable=True)
    opportunity_category: str = Column(String(100), nullable=True)  # One of 6 canonical categories
    ai_analysis: dict = Column(JSON, nullable=True)
    role_title: str = Column(String(255), nullable=True)
    department: str = Column(String(255), nullable=True)
    seniority: str = Column(String(100), nullable=True)
    location: str = Column(String(255), nullable=True)
    urgency: str = Column(String(50), default="Medium")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="signals")

    @property
    def company_name(self) -> str:
        """Provide company_name for Pydantic serialization."""
        return self.company.name if self.company else ""
