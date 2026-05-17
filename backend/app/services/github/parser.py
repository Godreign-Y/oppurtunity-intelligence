from datetime import datetime
from typing import List
from app.schemas.github import GitHubIssue


def parse_issues(response: dict, query: str) -> List[GitHubIssue]:
    issues = []

    for item in response.get("items", []):
        repo_parts = item["repository_url"].split("/")[-2:]

        created_at = datetime.fromisoformat(
            item["created_at"].replace("Z", "+00:00")
        ).replace(tzinfo=None)

        issues.append(
            GitHubIssue(
                github_issue_id=item["id"],
                title=item.get("title", ""),
                body=item.get("body", "") or "",
                repo_name=repo_parts[1],
                org_name=repo_parts[0],
                comments_count=item.get("comments", 0),
                labels=[label["name"] for label in item.get("labels", [])],
                created_at=created_at,
                source_url=item["html_url"],
                query_used=query,
            )
        )

    return issues
