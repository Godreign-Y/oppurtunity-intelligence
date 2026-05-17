"""
app/services/hiring/processor.py

Handles sanitization of raw job descriptions and extraction of tech stack signals.
"""

import re
from typing import List
from bs4 import BeautifulSoup

from app.config.keywords.tech_stack_keywords import TECH_STACK_KEYWORDS


def sanitize_text(raw_html: str) -> str:
    """Removes HTML tags and cleans up whitespace from text."""
    if not raw_html:
        return ""
        
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ")
    
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_tech_stack(text: str) -> List[str]:
    """Extracts target technology keywords from the given text."""
    detected_stack: List[str] = []
    text_lower = text.lower()
    
    for keyword in TECH_STACK_KEYWORDS:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, text_lower):
            detected_stack.append(keyword)
            
    return detected_stack
