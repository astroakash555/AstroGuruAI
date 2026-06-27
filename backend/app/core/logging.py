"""Structured logging configuration."""

import logging
import sys
from typing import Literal

from backend.app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure root logger based on application settings."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if settings.log_format == "json":
        formatter = logging.Formatter(
            fmt='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)


def get_logger(name: str, level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] | None = None) -> logging.Logger:
    """Return a named logger instance."""
    logger = logging.getLogger(name)
    if level:
        logger.setLevel(getattr(logging, level))
    return logger
