"""Bot service configuration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = [
    "BotSettings",
    "LogSettings",
    "bot_settings",
    "log_settings",
]

load_dotenv()

# Base directory for bot service
BASE_DIR = Path(__file__).parent
PLUGINS_DIR = BASE_DIR / "plugins"


class BotSettings(BaseSettings):
    """Bot service configuration."""

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore",
    )

    # Discord configuration
    discord_token: str = Field(..., validation_alias="DISCORD_TOKEN")
    """Discord API token (from DISCORD_TOKEN)."""
    discord_dev_guild_id: int | None = Field(default=None, validation_alias="DISCORD_DEV_GUILD_ID")
    """Discord Guild ID for development."""
    discord_dev_user_id: int | None = Field(default=None, validation_alias="DISCORD_DEV_USER_ID")
    """Discord User ID for development."""
    command_prefix: list[str] = ["!"]
    """Command prefix for bot commands."""
    presence_url: str = ""
    """Bot presence URL."""

    # API service configuration
    api_service_url: str = Field(default="http://localhost:8000", validation_alias="API_SERVICE_URL")
    """Base URL for the API service."""

    # Plugin configuration
    plugins_dir: Path = PLUGINS_DIR
    """Path to plugins directory."""

    # Environment
    environment: str = Field(default="dev", validation_alias="ENVIRONMENT")
    """Environment: dev, test, or prod."""
    debug: bool = Field(default=False, validation_alias="DEBUG")
    """Enable debug mode."""

    @field_validator("command_prefix")
    @classmethod
    def assemble_command_prefix(cls, value: list[str]) -> list[str]:
        """Assemble bot command prefix based on environment.

        Args:
            value: Default command prefix

        Returns:
            Assembled prefix list
        """
        env_prefixes = {
            "prod": "byte ",
            "test": "bit ",
            "dev": "nibble ",
        }
        environment = os.getenv("ENVIRONMENT", "dev")
        env_prefix = os.getenv("COMMAND_PREFIX", env_prefixes.get(environment, "nibble "))

        if env_prefix not in value:
            value.append(env_prefix)

        return value

    @field_validator("presence_url")
    @classmethod
    def assemble_presence_url(cls, value: str) -> str:  # noqa: ARG003
        """Assemble bot presence URL based on environment.

        Args:
            value: Default presence URL (unused)

        Returns:
            Assembled presence URL
        """
        env_urls = {
            "prod": "https://byte-bot.app/",
            "test": "https://dev.byte-bot.app/",
            "dev": "https://dev.byte-bot.app/",
        }
        environment = os.getenv("ENVIRONMENT", "dev")
        return os.getenv("PRESENCE_URL", env_urls.get(environment, "https://dev.byte-bot.app/"))


class LogSettings(BaseSettings):
    """Logging configuration for the bot service."""

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore",
    )

    level: int = 20  # INFO
    """Root log level."""
    discord_level: int = 30  # WARNING
    """Discord.py log level."""
    websockets_level: int = 30  # WARNING
    """Websockets log level."""
    asyncio_level: int = 20  # INFO
    """Asyncio log level."""
    httpx_level: int = 30  # WARNING
    """HTTPX log level."""
    format: str = "[[ %(asctime)s ]] - [[ %(name)s ]] - [[ %(levelname)s ]] - %(message)s"
    """Log format string."""
    file: Path | None = None
    """Log file path (optional)."""


def load_settings() -> tuple[BotSettings, LogSettings]:
    """Load bot settings.

    Returns:
        Tuple of (bot_settings, log_settings)

    Raises:
        ValidationError: If settings validation fails
    """
    try:
        bot = BotSettings()
        log = LogSettings()
    except ValidationError as error:
        print(f"Could not load settings. Error: {error!r}")  # noqa: T201
        raise

    return bot, log


# Initialize settings
bot_settings, log_settings = load_settings()
