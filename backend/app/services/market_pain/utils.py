"""
app/services/market_pain/utils.py

Utility functions shared across the market pain pipeline modules.
"""

import time
from datetime import datetime, timezone


def timestamp_from_utc(utc_float: float) -> str:
    """Convert a Unix timestamp float to ISO 8601 string."""
    if utc_float <= 0:
        return datetime.now(timezone.utc).isoformat()
    return datetime.fromtimestamp(utc_float, tz=timezone.utc).isoformat()


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max_length, adding ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def days_ago(utc_float: float) -> int:
    """Return how many days ago a Unix timestamp was."""
    if utc_float <= 0:
        return 0
    return int((time.time() - utc_float) / 86400)
