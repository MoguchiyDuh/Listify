import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from colorama import Fore, Style, init

from .config import settings

init(autoreset=True)

COLORS = {
    "DEBUG": Fore.CYAN,
    "INFO": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.MAGENTA + Style.BRIGHT,
}


def setup_logger(name: str, debug: bool = settings.DEBUG) -> logging.Logger:
    """Logger with colored console output and rotating file handler"""

    logger = logging.getLogger(name)

    # Clear any existing handlers
    logger.handlers.clear()

    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    class ColorFormatter(logging.Formatter):
        def format(self, record):
            if sys.stdout.isatty():  # Only color in terminal
                # Make a copy to avoid modifying the original record
                record = logging.makeLogRecord(record.__dict__)
                color = COLORS.get(record.levelname, "")
                record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
                record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
            return super().format(record)

    console_formatter = ColorFormatter(
        fmt="[%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with rotation (5MB max, 10 backup files)
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"{name}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10,
        encoding="utf-8"
    )
    file_handler.setLevel(level)

    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger
