"""Schemas module for data validation.

This module contains Pydantic models for validating incoming job posting data.
"""

from typing import List, Optional
from pydantic import BaseModel



class RawJobPosting(BaseModel):
    """Pydantic model representing a raw job posting from the API.
    
    Attributes:
        job_title (str): The title of the job.
        company_name (str): The name of the hiring company.
        raw_description (str): The unedited job description.
        posted_date (str | None): The date the job was posted or its string representation.
    """
    job_title: str
    company_name: str
    raw_description: str
    posted_date: str | None = None


class ProcessedJobSignal(BaseModel):
    """Pydantic model representing a processed and sanitized job posting.

    Attributes:
        job_title (str): The title of the job.
        company_name (str): The name of the hiring company.
        posted_date (str | None): The date the job was posted or its string representation.
        sanitized_description (str): The job description with all HTML tags and boilerplate removed.
        detected_tech_stack (List[str]): A list of extracted technology keywords found in the description.
    """
    job_title: str
    company_name: str
    posted_date: str | None = None
    sanitized_description: str
    detected_tech_stack: List[str]


class DecisionMaker(BaseModel):
    """Pydantic model representing a key decision maker at a company.

    Attributes:
        first_name (Optional[str]): First name of the decision maker.
        last_name (Optional[str]): Last name of the decision maker.
        title (Optional[str]): The exact job title of the person.
        email (Optional[str]): Email address of the person.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None


class EnrichedOpportunity(ProcessedJobSignal):
    """Pydantic model representing an enriched job opportunity with company and contact info.

    Attributes:
        company_domain (str): The domain of the hiring company.
        decision_makers (List[DecisionMaker]): List of key decision makers identified.
    """
    company_domain: str
    decision_makers: List[DecisionMaker]
