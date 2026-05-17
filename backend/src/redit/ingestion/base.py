"""Abstract Reddit ingestion interface."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from redit.models.discovery import GlobalFeed
from redit.models.reddit import (
    RawRedditPost,
    RedditSort,
)


class RedditSource(ABC):
    """
    Source-agnostic Reddit iterator.

    Supports:
    - global feeds
    - subreddit feeds
    - Reddit search
    """

    @abstractmethod
    async def iter_global_feed(
        self,
        feed: GlobalFeed,
        sort: RedditSort = "hot",
        limit: int = 25,
    ) -> AsyncIterator[RawRedditPost]:
        """
        Yield posts from:
        - r/all
        - r/popular
        """

        ...

    @abstractmethod
    async def iter_subreddit_feed(
        self,
        subreddit: str,
        sort: RedditSort = "new",
        limit: int = 25,
    ) -> AsyncIterator[RawRedditPost]:
        """
        Yield posts from subreddit feeds.
        """

        ...

    @abstractmethod
    async def iter_search(
        self,
        query: str,
        sort: RedditSort = "relevance",
        limit: int = 25,
    ) -> AsyncIterator[RawRedditPost]:
        """
        Yield posts from Reddit search.
        """

        ...

    async def close(self) -> None:
        """
        Release HTTP clients/resources.
        """

        return None