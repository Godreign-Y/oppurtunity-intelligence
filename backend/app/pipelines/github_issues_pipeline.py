"""
app/pipelines/github_issues_pipeline.py

Standalone GitHub Issues Intelligence Pipeline.

Fetches real GitHub issues using company name + tech keywords,
classifies each issue into one of the 6 canonical opportunity categories,
and stores results in the database.

Entry point: run_github_issues_pipeline(company_name, db)
"""

import logging
from typing import Any
from sqlalchemy.orm import Session

from app.config.keywords.github_issue_keywords import GITHUB_SEARCH_TECH_TERMS
from app.models.github_signal import GitHubSignal
from app.services.github.service import GitHubIngestionService, infer_github_opportunity_category

logger = logging.getLogger(__name__)

# Tech keywords used to build a compound GitHub search query for the company.
# Focuses on infrastructure, AI, DevOps — areas where consulting is valuable.
def _build_github_query(company_name: str) -> str:
    """
    Build a GitHub issues search query for a specific company.

    Searches for issues in repositories owned by or mentioning the company,
    combined with high-signal tech pain keywords.

    Args:
        company_name: Target company name.

    Returns:
        GitHub search query string.
    """
    tech_or = " OR ".join(GITHUB_SEARCH_TECH_TERMS[:6])
    return f'"{company_name}" ({tech_or}) is:issue is:open label:bug,performance,infrastructure'


def _infer_category_from_issue(title: str, labels: list[str]) -> str:
    """
    Infer the opportunity category from a GitHub issue's title and labels.

    Args:
        title: Issue title text.
        labels: List of GitHub label names.

    Returns:
        A canonical opportunity category string.
    """
    return infer_github_opportunity_category(title, labels)


async def run_github_issues_pipeline(
    company_name: str,
    db: Session,
) -> list[dict[str, Any]]:
    """
    Run the GitHub Issues Intelligence Pipeline for a specific company.

    Fetches real GitHub issues, assigns opportunity categories,
    and persists them to the database.

    Args:
        company_name: Target company to search issues for.
        db: Active SQLAlchemy database session.

    Returns:
        List of enriched issue dicts with opportunity_category field.
    """
    logger.info(f"[GitHubIssuesPipeline] Starting for company: {company_name}")

    try:
        service = GitHubIngestionService(db)
        query = _build_github_query(company_name)
        logger.info(f"[GitHubIssuesPipeline] Search query: {query}")

        issues = await service.ingest(query)
        logger.info(f"[GitHubIssuesPipeline] Fetched {len(issues)} issues")
    except Exception as exc:
        logger.error(f"[GitHubIssuesPipeline] Failed to fetch GitHub issues: {exc}")
        return []

    enriched: list[dict[str, Any]] = []
    for issue in issues:
        labels = issue.labels if hasattr(issue, "labels") and issue.labels else []
        category = _infer_category_from_issue(issue.title, labels)
        db_record = db.query(GitHubSignal).filter(
            GitHubSignal.external_id == str(issue.github_issue_id)
        ).first()
        if db_record and db_record.opportunity_category != category:
            db_record.opportunity_category = category
            db.commit()

        enriched.append({
            "id": issue.github_issue_id,
            "title": issue.title,
            "content": issue.body,
            "source_url": issue.source_url,
            "repo": issue.repo_name,
            "org": issue.org_name,
            "labels": labels,
            "comments": issue.comments_count,
            "created_at": str(issue.created_at),
            "opportunity_category": category,
            "source": "github_issues",
        })

    logger.info(
        f"[GitHubIssuesPipeline] Completed: {len(enriched)} issues enriched with opportunity categories"
    )
    return enriched
