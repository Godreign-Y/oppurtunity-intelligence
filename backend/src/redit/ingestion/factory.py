"""Factory for Reddit ingestion backends."""

from redit.config.settings import Settings
from redit.ingestion.base import RedditSource
from redit.ingestion.praw_source import PrawRedditSource
from redit.ingestion.public_json import PublicJsonRedditSource


def create_reddit_source(settings: Settings) -> RedditSource:
    """
    Build the configured Reddit source implementation.

    Switch via REDDIT_SOURCE without changing pipeline or services.
    """
    if settings.reddit_source == "public_json":
        return PublicJsonRedditSource(settings)

    if settings.reddit_source == "praw":
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            raise ValueError(
                "REDDIT_SOURCE=praw requires REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET.",
            )
        return PrawRedditSource(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )

    raise ValueError(f"Unknown REDDIT_SOURCE: {settings.reddit_source}")
