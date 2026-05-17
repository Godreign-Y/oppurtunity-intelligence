"""
app/models/hiring_signal.py

ORM model representing a tracked corporate hiring signal / job opening.
"""

import uuid
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class HiringSignal(Base):
    """
    Represents an open role or hiring signal (e.g. DevOps Engineeer, Cloud Migration Specialist)
    tracked to find technical modernization needs in target companies.
    """

    __tablename__ = "hiring_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    job_title = Column(String(255), nullable=False)
    posted_date = Column(String(100), nullable=True)
    sanitized_description = Column(Text, nullable=True)
    detected_tech_stack = Column(JSON, nullable=True)  # List[str]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="hiring_signals")
