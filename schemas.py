"""Schemas module for data validation.

This module contains Pydantic models for validating incoming job posting data.
"""

from typing import List
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

