"""Centralized logging configuration."""
import logging
import logging.config
import logging.handlers
from logging import Logger
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler  # noqa: F401
from rich.traceback import install

from src.byte.lib import settings

__all__ = [
    "setup_logging",
    "get_logger",
]

install(show_locals=True, theme="dracula")
console = Console()


def setup_logging() -> None:
    """Set up logging configuration based on the environment."""
    env = settings.project.ENVIRONMENT
    log_file_path = settings.log.FILE
    log_directory = log_file_path.parent

    if not Path(log_directory).exists():
        Path(log_directory).mkdir(parents=True, exist_ok=True)

    handlers = {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "simple",
            "filename": settings.BASE_DIR / "logs" / "byte.log",
            "maxBytes": 10485760,
            "backupCount": 3,
            "level": "INFO",
        },
        "syslog": {
            "class": "logging.handlers.SysLogHandler",
            "formatter": "simple",
            "address": "/dev/log",
            "level": "INFO",
        },
        "console": {
            "class": "rich.logging.RichHandler",
            "formatter": "simple",
            "level": "DEBUG",
        }
        if env == "dev"
        else {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "INFO",
        },
    }

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": settings.log.FORMAT,
            },
        },
        "handlers": handlers,
        "loggers": {
            "discord": {
                "level": settings.log.DISCORD_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "websockets": {
                "level": settings.log.WEBSOCKETS_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "asyncio": {
                "level": settings.log.ASYNCIO_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "root": {
                "level": "DEBUG" if settings.project.DEBUG else "INFO",
                "handlers": ["console", "file"] if env == "dev" else ["file", "syslog"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)


def get_logger(name: str = "__main__") -> Logger:
    """Get a logger with the specified name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The logger with the specified name.
    """
    return logging.getLogger(name)
