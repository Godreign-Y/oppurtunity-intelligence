"""
app/core/config.py

Application configuration loaded from environment variables using Pydantic Settings.
All external service credentials and runtime options are managed here.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Central settings class for the Opportunity Intelligence Platform.

    Loads values from environment variables or a .env file.
    """

    # --- App ---
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    # --- Database ---
    database_url: str = Field(default="", alias="DATABASE_URL")

    # --- Search APIs ---
    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")
    serper_api_key: str = Field(default="", alias="SERPER_API_KEY")

    # --- Web Extraction ---
    firecrawl_api_key: str = Field(default="", alias="FIRECRAWL_API_KEY")

    # --- LLM ---
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL"
    )
    llm_model: str = Field(default="openai/gpt-4o-mini", alias="LLM_MODEL")

    # --- Ingestions API Keys ---
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    serpapi_api_key: str = Field(default="", alias="SERPAPI_API_KEY")

    # --- GitHub ---
    GITHUB_TOKEN: str = Field(default="", alias="GITHUB_TOKEN")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "populate_by_name": True}


settings = Settings()


@lru_cache()
def get_settings() -> Settings:
    """Return the cached settings singleton (compatible with second-project services)."""
    return settings

