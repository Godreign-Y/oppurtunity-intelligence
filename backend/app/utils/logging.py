"""
app/utils/logging.py

Centralized logging configuration for the Opportunity Intelligence Platform.
Call setup_logging() once at application startup.

Supports optional file logging via the LOG_FILE environment variable.
"""

import logging
import os
import sys
from typing import Optional

from app.core.config import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_NOISY_LOGGERS = ("httpx", "httpcore", "urllib3", "feedparser")


def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure the root logger with consistent format.

    Outputs to stdout always. If settings.log_file is set, also writes to that file.
    Creates the log file directory if it does not exist.

    Args:
        level: Optional log level override (e.g. 'DEBUG', 'INFO').
               Defaults to the LOG_LEVEL setting from config.
    """
    log_level = (level or settings.log_level).upper()

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    # Optional file handler — uses LOG_FILE env var
    log_file = settings.log_file.strip()
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        format=_LOG_FORMAT,
        datefmt=_DATE_FORMAT,
        handlers=handlers,
        force=True,  # Override any previously configured root handlers
    )

    # Suppress noisy third-party loggers
    for noisy in _NOISY_LOGGERS:
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        f"Logging configured | level={log_level} | file={log_file or 'stdout-only'}"
    )
