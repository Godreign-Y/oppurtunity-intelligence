"""NVIDIA NIM OpenAI-compatible LLM client.

This standalone helper mirrors the app client configuration and uses
NVIDIA_API_KEY, NVIDIA_BASE_URL, and MODEL from backend/.env.
"""

from collections.abc import Iterable

from openai import APIError, BadRequestError, OpenAI

from app.core.config import settings


class NvidiaLLMClient:
    """Client wrapper for NVIDIA NIM chat completion models."""

    def __init__(self) -> None:
        if not settings.nvidia_api_key:
            raise RuntimeError("NVIDIA_API_KEY is not configured.")
        self.client = OpenAI(base_url=settings.nvidia_base_url, api_key=settings.nvidia_api_key)

    def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        top_p: float = 0.9,
        max_tokens: int = 600,
        extra_body: dict[str, object] | None = None,
    ) -> str:
        """Return a non-streamed chat completion from NVIDIA NIM."""
        try:
            completion = self.client.chat.completions.create(
                model=settings.model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                extra_body=extra_body,
                stream=False,
            )
        except BadRequestError as error:
            raise RuntimeError(f"NVIDIA rejected the LLM request: {error.message}") from error
        except APIError as error:
            raise RuntimeError(f"NVIDIA LLM request failed: {error.message}") from error
        content = completion.choices[0].message.content
        if content is None:
            raise RuntimeError(f"NVIDIA model {settings.model} returned no content")
        return content.strip()

    def stream_complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        top_p: float = 0.9,
        max_tokens: int = 600,
        extra_body: dict[str, object] | None = None,
    ) -> Iterable[str]:
        """Yield streamed content chunks from NVIDIA NIM."""
        completion = self.client.chat.completions.create(
            model=settings.model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            extra_body=extra_body,
            stream=True,
        )
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
