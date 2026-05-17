"""
GitHub ingestion service.
"""

from typing import List
from sqlalchemy.orm import Session

from app.services.github.client import GitHubClient
from app.services.github.parser import parse_issues
from app.schemas.github import GitHubIssue
from app.repositories.github_signal_repository import GitHubSignalRepository
from app.config.category_mapper import map_to_opportunity_category


def infer_github_opportunity_category(title: str, labels: list[str] | None = None) -> str:
    """Infer a canonical opportunity category from GitHub issue text."""
    combined = f"{title} {' '.join(labels or [])}".lower()
    if any(kw in combined for kw in ["llm", "ai", "ml", "model", "inference", "embedding", "rag"]):
        return map_to_opportunity_category("ai_ml_production_pain")
    if any(kw in combined for kw in ["mlops", "training", "gpu", "serving"]):
        return map_to_opportunity_category("mlops_scaling")
    if any(kw in combined for kw in ["migration", "legacy", "monolith", "rewrite", "refactor"]):
        return map_to_opportunity_category("migration_pain")
    if any(kw in combined for kw in ["scaling", "bottleneck", "memory", "performance", "latency"]):
        return map_to_opportunity_category("scaling_bottleneck")
    if any(kw in combined for kw in ["deployment", "ci/cd", "pipeline", "rollback", "build"]):
        return map_to_opportunity_category("deployment_failure")
    if any(kw in combined for kw in ["security", "vulnerability", "auth", "compliance"]):
        return map_to_opportunity_category("security_compliance_gap")
    if any(kw in combined for kw in ["cost", "billing", "expensive", "budget"]):
        return map_to_opportunity_category("cloud_cost_pressure")
    return map_to_opportunity_category("enterprise_reliability")

class GitHubIngestionService:
    """
    Service for fetching and storing GitHub signals.
    """

    def __init__(self, db: Session):
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
            category = infer_github_opportunity_category(issue.title, issue.labels)
            issue.opportunity_category = category
            self.repo.create(
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
                    "opportunity_category": category,
                }
            )

        return issues
