import datetime
from typing import Optional
from pydantic import BaseModel

class CompanyBase(BaseModel):
    name: str
    industry: Optional[str] = None
    is_product_based: bool = True
    description: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: int
    
    class Config:
        from_attributes = True

class FundingEventBase(BaseModel):
    amount: Optional[float] = None
    stage: Optional[str] = None
    source_url: Optional[str] = None
    raw_text: Optional[str] = None
    opportunity_score: Optional[int] = None

class FundingEventCreate(FundingEventBase):
    company_name: str # The pipeline will find or create the company

class FundingEventResponse(FundingEventBase):
    id: int
    company_id: int
    date: datetime.datetime

    class Config:
        from_attributes = True
