"""
app/schemas/hiring.py

Pydantic schemas for validation and JSON serialization of Hiring signals.
"""

import uuid
import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class HiringSignalBase(BaseModel):
    job_title: str
    posted_date: Optional[str] = None
    sanitized_description: Optional[str] = None
    detected_tech_stack: List[str] = []


class HiringSignalCreate(HiringSignalBase):
    company_name: str


class HiringSignalResponse(HiringSignalBase):
    id: uuid.UUID
    company_id: uuid.UUID
    company_name: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class HiringInsightsSchema(BaseModel):
    total_jobs: int
    top_skills: List[Dict[str, Any]]
    top_hiring: List[Dict[str, Any]]
