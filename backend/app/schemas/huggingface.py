"""
Schemas for Hugging Face data.
"""

from pydantic import BaseModel
from typing import List


class HFModelSignal(BaseModel):
    """
    Structured Hugging Face signal.
    """

    model_id: str
    downloads: int
    likes: int
    tags: List[str]
    pipeline_tag: str | None
    discussion_title: str | None
    discussion_content: str | None
    source_url: str