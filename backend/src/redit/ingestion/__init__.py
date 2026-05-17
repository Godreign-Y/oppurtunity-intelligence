"""Reddit data ingestion layer."""

from redit.ingestion.base import RedditSource
from redit.ingestion.factory import create_reddit_source

__all__ = ["RedditSource", "create_reddit_source"]
