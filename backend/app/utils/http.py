"""
app/utils/http.py

HTTP helper utilities with retry logic using tenacity.
Use these wrappers for all outbound HTTP calls that may be flaky.
"""

import httpx
import logging
from typing import Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
async def get_with_retry(
    url: str,
    headers: Optional[dict[str, str]] = None,
    params: Optional[dict[str, Any]] = None,
    timeout: float = 15.0,
) -> httpx.Response:
    """
    Perform an HTTP GET request with exponential backoff retry.

    Retries up to 3 times on httpx.HTTPError with 1–8 second waits.

    Args:
        url: Target URL.
        headers: Optional request headers.
        params: Optional query parameters.
        timeout: Request timeout in seconds.

    Returns:
        httpx.Response object.

    Raises:
        httpx.HTTPError: After all retries are exhausted.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, headers=headers or {}, params=params or {}, follow_redirects=True)
        response.raise_for_status()
        return response


@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
async def post_with_retry(
    url: str,
    json: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, str]] = None,
    timeout: float = 20.0,
) -> httpx.Response:
    """
    Perform an HTTP POST request with exponential backoff retry.

    Args:
        url: Target URL.
        json: JSON payload dict.
        headers: Optional request headers.
        timeout: Request timeout in seconds.

    Returns:
        httpx.Response object.

    Raises:
        httpx.HTTPError: After all retries are exhausted.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, json=json or {}, headers=headers or {})
        response.raise_for_status()
        return response
