import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from app.core.config import settings

# Constants
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 3
LOG_FILE = "Listify.log"

# Color codes
COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[35m",  # Magenta
    "RESET": "\033[0m",  # Reset
}


class ColorFormatter(logging.Formatter):

    def format(self, record):
        if sys.stdout.isatty():  # Only colorize if output is a terminal
            levelname = record.levelname
            if levelname in COLORS:
                record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
                record.msg = f"{COLORS[levelname]}{record.msg}{COLORS['RESET']}"
        return super().format(record)


def setup_logger(
    name: str,
    debug: bool = settings.DEBUG,
    log_file: Optional[str] = LOG_FILE,
) -> logging.Logger:

    logger = logging.getLogger(name)

    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logger.level)

    console_formatter = ColorFormatter(
        fmt="[%(levelname)s] %(asctime)s - %(name)s: %(message)s", datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)

        file_formatter = logging.Formatter(
            fmt="[%(levelname)s] %(asctime)s - %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger
