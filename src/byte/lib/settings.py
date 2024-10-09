"""Project Settings."""
from __future__ import annotations

import os
from pathlib import Path  # noqa: TCH003
from typing import Final

from dotenv import load_dotenv
from pydantic import ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src import utils
from src.__metadata__ import __version__ as version

__all__ = [
    "discord",
    "log",
    "project",
    "DiscordSettings",
    "LogSettings",
    "ProjectSettings",
]

load_dotenv()

DEFAULT_MODULE_NAME: str = "src"
BASE_DIR: Final = utils.module_to_os_path(DEFAULT_MODULE_NAME)
PLUGINS_DIR: Final = utils.module_to_os_path("src.byte.plugins")


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
    PLUGINS_LOC: Path = PLUGINS_DIR
    """Base Path to plugins directory."""
    PLUGINS_DIRS: list[Path] = [f"{PLUGINS_DIR}"]
    """Directories to search for plugins."""
    PRESENCE_URL: str = ""

    @field_validator("COMMAND_PREFIX")
    @classmethod
    def assemble_command_prefix(cls, value: str) -> list[str]:
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
        value.append(os.getenv("COMMAND_PREFIX", env_urls[environment]))
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
def load_settings() -> (
    tuple[
        DiscordSettings,
        LogSettings,
        ProjectSettings,
    ]
):
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
