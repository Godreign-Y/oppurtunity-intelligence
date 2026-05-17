"""PRAW-based Reddit source (future swap-in when API credentials are available)."""

from collections.abc import AsyncIterator

from redit.ingestion.base import RedditSource
from redit.models.discovery import GlobalFeed
from redit.models.reddit import RawRedditPost, RedditSort


class PrawRedditSource(RedditSource):
    """
    Placeholder for official Reddit API via PRAW.

    TODO: Implement global feed, search, and RawRedditPost mapping when credentials exist.
    """

    def __init__(self, client_id: str, client_secret: str, user_agent: str) -> None:
        """Store credentials for future PRAW session."""
        self._client_id = client_id
        self._client_secret = client_secret
        self._user_agent = user_agent

    async def iter_global_feed(
        self,
        feed: GlobalFeed,
        sort: RedditSort = "hot",
        limit: int = 25,
    ) -> AsyncIterator[RawRedditPost]:
        """Not implemented until Reddit API credentials are available."""
        raise NotImplementedError(
            "PRAW ingestion is not implemented. Set REDDIT_SOURCE=public_json.",
        )
        yield  # pragma: no cover

    async def iter_search(
        self,
        query: str,
        sort: RedditSort = "relevance",
        limit: int = 25,
    ) -> AsyncIterator[RawRedditPost]:
        """Not implemented until Reddit API credentials are available."""
        raise NotImplementedError(
            "PRAW ingestion is not implemented. Set REDDIT_SOURCE=public_json.",
        )
        yield  # pragma: no cover
