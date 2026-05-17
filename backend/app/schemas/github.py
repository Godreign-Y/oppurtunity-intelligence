"""
Schemas for GitHub API responses.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import List


class GitHubIssue(BaseModel):
    """
    Represents a parsed GitHub issue.
    """

    github_issue_id: int
    title: str
    body: str
    repo_name: str
    org_name: str
    comments_count: int
    labels: List[str]
    created_at: datetime
    source_url: str
    query_used: str
    opportunity_category: str | None = None
