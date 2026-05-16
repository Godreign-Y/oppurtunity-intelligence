"""
app/schemas/company.py

Pydantic schemas for Company request/response serialization.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class CompanyCreate(BaseModel):
    """Schema for creating a new company record."""

    name: str
    domain: Optional[str] = None


class CompanyResponse(BaseModel):
    """
    API response schema for a Company record.

    Attributes:
        id: Unique company UUID.
        name: Company name.
        domain: Company domain.
        ats_platform: Detected ATS platform.
        blog_url: Discovered engineering blog URL.
        created_at: Record creation time.
    """

    id: uuid.UUID
    name: str
    domain: Optional[str] = None
    ats_platform: Optional[str] = None
    blog_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
