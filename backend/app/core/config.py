"""
Application configuration using pydantic-settings.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.
    """
    GITHUB_TOKEN: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    """
    Returns cached settings.

    Returns:
        Settings: configuration object
    """
    return Settings()