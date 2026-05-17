"""
GitHub API client using async HTTP requests.
"""

import httpx
from app.core.config import get_settings


class GitHubClient:
    """
    Handles communication with GitHub API.
    """

    BASE_URL = "https://api.github.com"

    def __init__(self) -> None:
        """
        Initialize GitHub client with authentication.
        """
        settings = get_settings()
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "Opportunity-Intel-App"
        }
        if settings.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    async def search_issues(self, query: str) -> dict:
        """
        Search GitHub issues using query.

        Args:
            query (str): search query

        Returns:
            dict: GitHub API response
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/search/issues",
                params={"q": query},
                headers=self.headers,
                timeout=30.0,
            )

        response.raise_for_status()
        return response.json()