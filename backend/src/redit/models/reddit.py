"""Reddit post domain models."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, computed_field

RedditSort = Literal["hot", "new", "top", "rising", "relevance"]


class RawRedditPost(BaseModel):
    """Normalized Reddit post used by the pipeline (source-agnostic)."""

    id: str = Field(description="Reddit post fullname or id.")
    subreddit: str
    title: str
    body: str = Field(default="", description="Post selftext or empty for link posts.")
    score: int = Field(ge=0)
    created_utc: float = Field(description="Unix timestamp from Reddit.")
    permalink: str
    url: str | None = None
    author: str | None = None
    num_comments: int = 0

    @computed_field  # type: ignore[prop-decorator]
    @property
    def combined_text(self) -> str:
        """Title and body concatenated for filtering."""
        return f"{self.title}\n{self.body}".strip()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def created_at(self) -> datetime:
        """Post creation time as timezone-aware UTC datetime."""
        return datetime.fromtimestamp(self.created_utc, tz=timezone.utc)
