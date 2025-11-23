"""Centralized logging configuration."""

import logging
import logging.config
import logging.handlers
from logging import Logger
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler  # noqa: F401
from rich.traceback import install

from byte_bot.config import bot_settings, log_settings

__all__ = [
    "get_logger",
    "setup_logging",
]

install(show_locals=True, theme="dracula")
console = Console()


def setup_logging() -> None:
    """Set up logging configuration based on the environment."""
    env = bot_settings.environment
    log_file_path = log_settings.file

    if log_file_path:
        log_directory = log_file_path.parent
        if not Path(log_directory).exists():
            Path(log_directory).mkdir(parents=True, exist_ok=True)

    handlers = {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "simple",
            "filename": log_file_path or Path("logs") / "byte.log",
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
                "format": log_settings.format,
            },
        },
        "handlers": handlers,
        "loggers": {
            "discord": {
                "level": log_settings.discord_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "httpcore": {
                "level": log_settings.httpx_level,  # Using httpx_level for httpcore too
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "httpx": {
                "level": log_settings.httpx_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "websockets": {
                "level": log_settings.websockets_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "asyncio": {
                "level": log_settings.asyncio_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "root": {
                "level": "DEBUG" if bot_settings.debug else "INFO",
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
