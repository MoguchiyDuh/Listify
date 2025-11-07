import logging
import sys

from colorama import Fore, Style, init

init(autoreset=True)

COLORS = {
    "DEBUG": Fore.CYAN,
    "INFO": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.MAGENTA + Style.BRIGHT,
}


def setup_logger(name: str, debug: bool = False) -> logging.Logger:
    """Simple logger with colored console output"""

    logger = logging.getLogger(name)

    # Clear any existing handlers
    logger.handlers.clear()

    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Simple formatter with colors
    class ColorFormatter(logging.Formatter):
        def format(self, record):
            if sys.stdout.isatty():  # Only color in terminal
                color = COLORS.get(record.levelname, "")
                record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
                record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
            return super().format(record)

    formatter = ColorFormatter(
        fmt="[%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.propagate = False
    return logger
