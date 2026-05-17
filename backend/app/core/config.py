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
    log_file: str = Field(default="", alias="LOG_FILE")  # Empty = stdout only; set path in production
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")
    trusted_hosts: str = Field(default="localhost,127.0.0.1,*.localhost,testserver", alias="TRUSTED_HOSTS")
    security_headers_enabled: bool = Field(default=True, alias="SECURITY_HEADERS_ENABLED")
    enforce_https: bool = Field(default=False, alias="ENFORCE_HTTPS")
    rate_limit_per_minute: int = Field(default=120, alias="RATE_LIMIT_PER_MINUTE")
    rate_limit_salt: str = Field(default="change-me-in-production", alias="RATE_LIMIT_SALT")

    # --- Database ---
    database_url: str = Field(default="", alias="DATABASE_URL")

    # --- Search APIs ---
    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")
    serper_api_key: str = Field(default="", alias="SERPER_API_KEY")

    # --- Web Extraction ---
    firecrawl_api_key: str = Field(default="", alias="FIRECRAWL_API_KEY")

    # --- LLM (NVIDIA NIM) ---
    nvidia_api_key: str = Field(default="", alias="NVIDIA_API_KEY")
    nvidia_base_url: str = Field(
        default="https://integrate.api.nvidia.com/v1", alias="NVIDIA_BASE_URL"
    )
    model: str = Field(default="", alias="MODEL")

    # --- Ingestion API Keys ---
    serpapi_api_key: str = Field(default="", alias="SERPAPI_API_KEY")
    adzuna_app_id: str = Field(default="", alias="ADZUNA_APP_ID")
    adzuna_app_key: str = Field(default="", alias="ADZUNA_APP_KEY")
    hunter_api_key: str = Field(default="", alias="HUNTER_API_KEY")

    # --- GitHub ---
    GITHUB_TOKEN: str = Field(default="", alias="GITHUB_TOKEN")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def trusted_hosts_list(self) -> list[str]:
        """Parse TRUSTED_HOSTS string into a list."""
        return [host.strip() for host in self.trusted_hosts.split(",") if host.strip()]

    model_config = {"env_file": ".env", "populate_by_name": True, "extra": "ignore"}


settings = Settings()


@lru_cache()
def get_settings() -> Settings:
    """Return the cached settings singleton."""
    return settings
