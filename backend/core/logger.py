import logging
import sys
from pathlib import Path

import structlog
from structlog.types import EventDict, Processor

from .config import settings


def setup_logger(name: str = "listify") -> None:
    """Configure structlog for structured JSON logging"""

    # Shared processors
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.DEBUG:
        # Development: Colorful console output
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # Production: JSON output for machine parsing
        processors.extend([
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ])

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Standard logging configuration for integration with other libraries
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger for a specific module"""
    return structlog.get_logger(name)
