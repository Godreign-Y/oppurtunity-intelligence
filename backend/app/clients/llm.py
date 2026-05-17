"""
Shared OpenAI-compatible LLM client factory.

NVIDIA NIM is the only LLM provider used by the pipeline.
"""

from openai import AsyncOpenAI

from app.core.config import settings


def get_llm_client() -> AsyncOpenAI | None:
    """Return the configured NVIDIA NIM async client, if credentials exist."""
    if settings.nvidia_api_key:
        return AsyncOpenAI(
            api_key=settings.nvidia_api_key,
            base_url=settings.nvidia_base_url,
        )

    return None


def get_llm_model() -> str:
    """Return the configured NVIDIA NIM model name."""
    return settings.model
