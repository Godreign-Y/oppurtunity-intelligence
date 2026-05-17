"""
app/models/company.py

ORM model representing a tracked product-based company.
"""

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base


class Company(Base):
    """
    Represents a company being monitored by the intelligence platform.

    Attributes:
        id: UUID primary key.
        name: Human-readable company name.
        domain: Company website domain.
        ats_platform: Detected ATS platform (greenhouse, lever, ashby, workday).
        blog_url: Engineering blog URL if discovered.
        created_at: Record creation timestamp.
        signals: Relationship to extracted signals.
    """

    __tablename__ = "companies"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: str = Column(String(255), nullable=False, unique=True, index=True)
    domain: str = Column(String(255), nullable=True)
    ats_platform: str = Column(String(50), nullable=True)
    blog_url: str = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    signals = relationship("Signal", back_populates="company", cascade="all, delete-orphan")
    market_pain_signals = relationship("MarketPainSignal", back_populates="company", cascade="all, delete-orphan")
    funding_events = relationship("FundingEvent", back_populates="company", cascade="all, delete-orphan")
    hiring_signals = relationship("HiringSignal", back_populates="company", cascade="all, delete-orphan")
