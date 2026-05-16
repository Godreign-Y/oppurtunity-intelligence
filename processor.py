"""Data processing and transformation module.

This module handles the sanitization of raw job descriptions and the extraction
of critical technology stack signals from the parsed text.
"""

import re
from typing import List

from bs4 import BeautifulSoup

from schemas import ProcessedJobSignal, RawJobPosting

TARGET_KEYWORDS = [
    "AWS", "GCP", "Azure", "Kubernetes", "Docker", "Python", "React", 
    "Node.js", "Legacy", "Migration", "Microservices", "CI/CD"
]


def sanitize_text(raw_html: str) -> str:
    """Removes HTML tags and cleans up whitespace from text.

    Args:
        raw_html (str): The raw text or HTML string.

    Returns:
        str: The sanitized plain text string.
    """
    if not raw_html:
        return ""
        
    # Strip HTML tags using BeautifulSoup
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ")
    
    # Clean up excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_tech_stack(text: str) -> List[str]:
    """Extracts target technology keywords from the given text.

    Scans the provided text case-insensitively for a predefined list of
    technology stack keywords and returns the unique matches found.

    Args:
        text (str): The text to be scanned for keywords.

    Returns:
        List[str]: A list of identified technology keywords.
    """
    detected_stack: List[str] = []
    text_lower = text.lower()
    
    for keyword in TARGET_KEYWORDS:
        # Use word boundaries to prevent partial matches (e.g., matching "CI/CD" accurately)
        # Note: Some keywords like Node.js have special chars, so escaping is safe.
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, text_lower):
            detected_stack.append(keyword)
            
    return detected_stack


def process_jobs(raw_jobs: List[RawJobPosting]) -> List[ProcessedJobSignal]:
    """Processes a list of raw job postings into processed job signals.

    Sanitizes the job description by removing HTML and extracts the tech stack
    keywords based on the target keyword list.

    Args:
        raw_jobs (List[RawJobPosting]): A list of unparsed, raw job postings.

    Returns:
        List[ProcessedJobSignal]: A list of clean, processed job signals.
    """
    processed_jobs: List[ProcessedJobSignal] = []
    
    for job in raw_jobs:
        sanitized_desc = sanitize_text(job.raw_description)
        tech_stack = extract_tech_stack(sanitized_desc)
        
        processed_signal = ProcessedJobSignal(
            job_title=job.job_title,
            company_name=job.company_name,
            posted_date=job.posted_date,
            sanitized_description=sanitized_desc,
            detected_tech_stack=tech_stack
        )
        processed_jobs.append(processed_signal)
        
    return processed_jobs
