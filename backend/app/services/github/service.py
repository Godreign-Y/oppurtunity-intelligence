"""
GitHub ingestion service.
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.github.client import GitHubClient
from app.services.github.parser import parse_issues
from app.schemas.github import GitHubIssue
from app.repositories.github_signal_repository import GitHubSignalRepository

class GitHubIngestionService:
    """
    Service for fetching and storing GitHub signals.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = GitHubClient()
        self.repo = GitHubSignalRepository(db)

    async def ingest(self, query: str) -> List[GitHubIssue]:
        """
        Fetch and store GitHub issues.

        Args:
            query (str): search query

        Returns:
            List[GitHubIssue]
        """
        response = await self.client.search_issues(query)
        issues = parse_issues(response, query)

        for issue in issues:
            await self.repo.create(
                {
                    "external_id": str(issue.github_issue_id),
                    "title": issue.title,
                    "content": issue.body,
                    "source_url": issue.source_url,
                    "created_at": issue.created_at,
                    "metadata_json": {
                        "repo": issue.repo_name,
                        "org": issue.org_name,
                        "comments": issue.comments_count,
                        "labels": issue.labels,
                        "query": issue.query_used,
                    },
                }
            )

        return issues
