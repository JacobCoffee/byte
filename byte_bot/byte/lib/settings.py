"""Project Settings."""

from __future__ import annotations

import os
from pathlib import Path  # noqa: TC003
from typing import Final

from dotenv import load_dotenv
from litestar.utils.module_loader import module_to_os_path
from pydantic import ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from byte_bot.__metadata__ import __version__ as version

__all__ = [
    "DiscordSettings",
    "LogSettings",
    "ProjectSettings",
    "discord",
    "log",
    "project",
]

load_dotenv()

DEFAULT_MODULE_NAME: str = "byte_bot"
BASE_DIR: Final = module_to_os_path(DEFAULT_MODULE_NAME)
PLUGINS_DIR: Final = module_to_os_path("byte_bot.byte.plugins")


class DiscordSettings(BaseSettings):
    """Discord Settings."""

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_prefix="DISCORD_", extra="ignore")

    TOKEN: str
    """Discord API token."""
    COMMAND_PREFIX: list[str] = ["!"]
    """Command prefix for bot commands."""
    DEV_GUILD_ID: int
    """Discord Guild ID for development."""
    DEV_USER_ID: int
    """Discord User ID for development."""
    DEV_GUILD_INTERNAL_ID: int = 1136100160510902272
    """Internal channel ID for the development guild."""
    PLUGINS_LOC: Path = PLUGINS_DIR
    """Base Path to plugins directory."""
    PLUGINS_DIRS: list[Path] = [PLUGINS_DIR]
    """Directories to search for plugins."""
    PRESENCE_URL: str = ""

    @field_validator("COMMAND_PREFIX")
    @classmethod
    def assemble_command_prefix(cls, value: list[str]) -> list[str]:
        """Assembles the bot command prefix based on the environment.

        Args:
            value: Default value of ``COMMAND_PREFIX``. Currently ``["!"]``

        Returns:
            The assembled prefix string.
        """
        env_urls = {
            "prod": "byte ",
            "test": "bit ",
            "dev": "nibble ",
        }
        environment = os.getenv("ENVIRONMENT", "dev")
        # Add env specific command prefix in addition to the default "!"
        env_prefix = os.getenv("COMMAND_PREFIX", env_urls[environment])
        if env_prefix not in value:
            value.append(env_prefix)
        return value

    @field_validator("PRESENCE_URL")
    @classmethod
    def assemble_presence_url(cls, value: str) -> str:  # noqa: ARG003
        """Assembles the bot presence url based on the environment.

        Args:
            value: Not used.

        Returns:
            The assembled prefix string.
        """
        env_urls = {
            "prod": "https://byte-bot.app/",
            "test": "https://dev.byte-bot.app/",
            "dev": "https://dev.byte-bot.app/",
        }
        environment = os.getenv("ENVIRONMENT", "dev")
        return os.getenv("PRESENCE_URL", env_urls[environment])


class LogSettings(BaseSettings):
    """Logging config for the Project."""

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_prefix="LOG_", extra="ignore")

    LEVEL: int = 20
    """Stdlib log levels.

    Only emit logs at this level, or higher.
    """
    DISCORD_LEVEL: int = 30
    """Sets the log level for the discord.py library."""
    WEBSOCKETS_LEVEL: int = 30
    """Sets the log level for the websockets library."""
    ASYNCIO_LEVEL: int = 20
    """Sets the log level for the asyncio library."""
    HTTP_CORE_LEVEL: int = 20
    """Sets the log level for the httpcore library. (Used in cert. validation)"""
    HTTPX_LEVEL: int = 30
    """Sets the log level for the httpx library."""
    FORMAT: str = "[[ %(asctime)s ]] - [[ %(name)s ]] - [[ %(levelname)s ]] - %(message)s"
    """Log format string."""
    FILE: Path = BASE_DIR / "logs" / "byte.log"
    """Log file path."""


class ProjectSettings(BaseSettings):
    """Project Settings."""

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

    DEBUG: bool = False
    """Run app with ``debug=True``."""
    ENVIRONMENT: str = "prod"
    """``dev``, ``prod``, ``test``, etc."""
    VERSION: str = version
    """The current version of the application."""


# noinspection PyShadowingNames
def load_settings() -> tuple[
    DiscordSettings,
    LogSettings,
    ProjectSettings,
]:
    """Load Settings file.

    Returns:
        Settings: application settings
    """
    try:
        """Override Application reload dir."""

        discord: DiscordSettings = DiscordSettings.model_validate({})
        log: LogSettings = LogSettings.model_validate({})
        project: ProjectSettings = ProjectSettings.model_validate({})

    except ValidationError as error:
        print(f"Could not load settings. Error: {error!r}")  # noqa: T201
        raise error from error
    return (
        discord,
        log,
        project,
    )


(
    discord,
    log,
    project,
) = load_settings()
