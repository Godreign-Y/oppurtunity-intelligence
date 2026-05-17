"""
app/models/funding_event.py

ORM model representing a tracked corporate funding round.
"""

import uuid
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class FundingEvent(Base):
    """
    Represents a corporate funding event (e.g. Series A, B, Seed)
    tracked for targeted consulting opportunities.
    """

    __tablename__ = "funding_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=True)  # In Millions USD
    stage = Column(String(100), nullable=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    source_url = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    opportunity_score = Column(Integer, default=10)

    company = relationship("Company", back_populates="funding_events")
