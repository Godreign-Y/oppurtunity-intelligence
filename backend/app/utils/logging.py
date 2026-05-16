"""
app/utils/logging.py

Centralized logging configuration for the Opportunity Intelligence Platform.
Call setup_logging() once at application startup.
"""

import logging
import sys
from typing import Optional

from app.core.config import settings


def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure root logger with a consistent format.

    Args:
        level: Optional log level override (e.g. 'DEBUG', 'INFO').
               Defaults to the LOG_LEVEL setting from config.
    """
    log_level = (level or settings.log_level).upper()

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Suppress noisy third-party loggers
    for noisy in ("httpx", "httpcore", "urllib3", "feedparser"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        f"Logging configured at level: {log_level}"
    )
