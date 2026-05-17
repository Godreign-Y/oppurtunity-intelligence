"""
app/schemas/funding.py

Pydantic schemas for validation and JSON serialization of Funding round signals.
"""

import uuid
import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str
    industry: Optional[str] = None
    is_product_based: bool = True
    description: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class FundingEventBase(BaseModel):
    amount: Optional[float] = None
    stage: Optional[str] = None
    source_url: Optional[str] = None
    raw_text: Optional[str] = None
    opportunity_score: Optional[int] = None


class FundingEventCreate(FundingEventBase):
    company_name: str


class FundingEventResponse(FundingEventBase):
    id: uuid.UUID
    company_id: uuid.UUID
    company_name: Optional[str] = None
    date: datetime.datetime

    class Config:
        from_attributes = True


class FundingInsightsSchema(BaseModel):
    total_funding: float
    average_funding: float
    events_count: int
    stage_distribution: List[Dict[str, Any]]
    top_funded: List[Dict[str, Any]]
