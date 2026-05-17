"""
app/models/pipeline_run.py

ORM model representing an asynchronous pipeline run.
"""

from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_name: str = Column(String(255), nullable=False, index=True)
    status: str = Column(String(50), nullable=False, default="pending") # pending, running, completed, failed
    pipelines_selected: list = Column(JSON, default=list)
    results: dict = Column(JSON, nullable=True) # stores final output/AI inference
    errors: dict = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
