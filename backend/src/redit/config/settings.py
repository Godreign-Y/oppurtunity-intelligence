"""Environment-backed application settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from redit.models.discovery import GlobalFeed

DEFAULT_DISCOVERY_FEEDS: list[GlobalFeed] = ["all", "popular"]

DEFAULT_SEARCH_QUERIES: list[str] = [
    "AI SaaS software frustration",
    "LLM API tool complaint",
    "startup product workflow pain",
]


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "redit"
    app_env: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    reddit_source: Literal["public_json", "praw"] = "public_json"
    reddit_user_agent: str = Field(
        default="redit-pain-intel/0.1 (contact: dev@localhost)",
        description="Required User-Agent for Reddit HTTP requests.",
    )
    reddit_request_timeout_seconds: float = 30.0
    reddit_request_delay_seconds: float = 1.0

    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None

    discovery_feeds: str | None = None
    discovery_search_queries: str | None = None

    min_text_length: int = 50
    min_upvotes: int = 5
    recency_days: int = 30

    sentence_transformer_model: str = "all-MiniLM-L6-v2"
    tech_similarity_min: float = 0.32
    tech_similarity_margin_min: float = 0.05
    frustration_detection_threshold: float = 0.55
    workflow_pain_keywords: str | None = None
    min_business_relevance: float = 0.2

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def discovery_feed_list(self) -> list[GlobalFeed]:
        """Global feeds to ingest (all, popular)."""
        if self.discovery_feeds:
            feeds = [f.strip().lower() for f in self.discovery_feeds.split(",") if f.strip()]
            return [f for f in feeds if f in ("all", "popular")]  # type: ignore[misc]
        return list(DEFAULT_DISCOVERY_FEEDS)

    @property
    def search_query_list(self) -> list[str]:
        """Default tech/product search queries for discovery."""
        if self.discovery_search_queries:
            return [q.strip() for q in self.discovery_search_queries.split("|") if q.strip()]
        return list(DEFAULT_SEARCH_QUERIES)

    @property
    def workflow_keyword_list(self) -> list[str]:
        """Workflow pain keywords from env or defaults."""
        defaults = [
            "manually",
            "workaround",
            "our company",
            "our team",
            "production",
            "enterprise",
            "compliance",
            "workflow",
            "can't deploy",
            "cannot deploy",
            "blocked us",
            "waste of time",
        ]
        if self.workflow_pain_keywords:
            return [k.strip() for k in self.workflow_pain_keywords.split(",") if k.strip()]
        return defaults


@lru_cache
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()
