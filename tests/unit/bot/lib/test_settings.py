"""Tests for bot settings module."""

from __future__ import annotations

from pathlib import Path

import pytest

from byte_bot.lib.settings import (
    DiscordSettings,  # type: ignore[attr-defined]
    LogSettings,  # type: ignore[attr-defined]
    ProjectSettings,  # type: ignore[attr-defined]
    load_settings,
)


class TestDiscordSettings:
    """Tests for DiscordSettings."""

    def test_discord_settings_loads_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test DiscordSettings loads from environment variables."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_discord_token_12345")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "987654321")
        monkeypatch.setenv("DISCORD_DEV_USER_ID", "123456789")

        settings = DiscordSettings()  # type: ignore[call-arg]

        assert settings.TOKEN == "test_discord_token_12345"
        assert settings.DEV_GUILD_ID == 987654321
        assert settings.DEV_USER_ID == 123456789

    def test_discord_settings_default_command_prefix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test default command prefix includes ! and env-specific prefix."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "123")
        monkeypatch.setenv("DISCORD_DEV_USER_ID", "456")
        monkeypatch.setenv("ENVIRONMENT", "dev")

        settings = DiscordSettings()

        assert "!" in settings.COMMAND_PREFIX
        assert "nibble " in settings.COMMAND_PREFIX  # dev environment prefix

    def test_discord_settings_command_prefix_prod(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test command prefix for production environment."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "123")
        monkeypatch.setenv("DISCORD_DEV_USER_ID", "456")
        monkeypatch.setenv("ENVIRONMENT", "prod")

        settings = DiscordSettings()

        assert "byte " in settings.COMMAND_PREFIX

    def test_discord_settings_command_prefix_test(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test command prefix for test environment."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "123")
        monkeypatch.setenv("DISCORD_DEV_USER_ID", "456")
        monkeypatch.setenv("ENVIRONMENT", "test")

        settings = DiscordSettings()

        assert "bit " in settings.COMMAND_PREFIX

    def test_discord_settings_custom_command_prefix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test custom command prefix from environment."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "123")
        monkeypatch.setenv("DISCORD_DEV_USER_ID", "456")
        monkeypatch.setenv("COMMAND_PREFIX", "custom>")

        settings = DiscordSettings()

        assert "custom>" in settings.COMMAND_PREFIX

    def test_discord_settings_presence_url_dev(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test presence URL for dev environment."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "123")
        monkeypatch.setenv("DISCORD_DEV_USER_ID", "456")
        monkeypatch.setenv("ENVIRONMENT", "dev")

        settings = DiscordSettings()

        assert settings.PRESENCE_URL == "https://dev.byte-bot.app/"

    def test_discord_settings_presence_url_prod(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test presence URL for prod environment."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "123")
        monkeypatch.setenv("DISCORD_DEV_USER_ID", "456")
        monkeypatch.setenv("ENVIRONMENT", "prod")

        settings = DiscordSettings()

        assert settings.PRESENCE_URL == "https://byte-bot.app/"

    def test_discord_settings_presence_url_test(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test presence URL for test environment."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "123")
        monkeypatch.setenv("DISCORD_DEV_USER_ID", "456")
        monkeypatch.setenv("ENVIRONMENT", "test")

        settings = DiscordSettings()

        assert settings.PRESENCE_URL == "https://dev.byte-bot.app/"

    def test_discord_settings_custom_presence_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test custom presence URL from environment."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "123")
        monkeypatch.setenv("DISCORD_DEV_USER_ID", "456")
        monkeypatch.setenv("PRESENCE_URL", "https://custom.example.com/")

        settings = DiscordSettings()

        assert settings.PRESENCE_URL == "https://custom.example.com/"

    def test_discord_settings_plugins_dir_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test plugins directory defaults."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "123")
        monkeypatch.setenv("DISCORD_DEV_USER_ID", "456")

        settings = DiscordSettings()

        assert isinstance(settings.PLUGINS_LOC, Path)
        assert isinstance(settings.PLUGINS_DIRS, list)
        assert len(settings.PLUGINS_DIRS) > 0

    def test_discord_settings_dev_guild_internal_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test dev guild internal ID has default value."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "123")
        monkeypatch.setenv("DISCORD_DEV_USER_ID", "456")

        settings = DiscordSettings()

        assert settings.DEV_GUILD_INTERNAL_ID == 1136100160510902272

    def test_discord_settings_token_required(self) -> None:
        """Test TOKEN field is required and populated."""
        settings = DiscordSettings()

        # Token should be populated from .env
        assert hasattr(settings, "TOKEN")
        assert isinstance(settings.TOKEN, str)
        assert len(settings.TOKEN) > 0

    def test_discord_settings_case_sensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test settings are case sensitive."""
        # Lowercase env var should not be read (case_sensitive=True)
        monkeypatch.setenv("discord_token", "lowercase_token")
        monkeypatch.setenv("DISCORD_TOKEN", "UPPERCASE_TOKEN")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "123")
        monkeypatch.setenv("DISCORD_DEV_USER_ID", "456")

        settings = DiscordSettings()

        assert settings.TOKEN == "UPPERCASE_TOKEN"


class TestLogSettings:
    """Tests for LogSettings."""

    def test_log_settings_has_expected_fields(self) -> None:
        """Test LogSettings has expected log levels."""
        settings = LogSettings()

        # Verify all log level fields exist and are integers
        assert isinstance(settings.LEVEL, int)
        assert isinstance(settings.DISCORD_LEVEL, int)
        assert isinstance(settings.WEBSOCKETS_LEVEL, int)
        assert isinstance(settings.ASYNCIO_LEVEL, int)
        assert isinstance(settings.HTTP_CORE_LEVEL, int)
        assert isinstance(settings.HTTPX_LEVEL, int)
        # Discord/websockets/httpx should have higher (less verbose) levels
        assert settings.DISCORD_LEVEL >= settings.LEVEL
        assert settings.WEBSOCKETS_LEVEL >= settings.LEVEL

    def test_log_settings_custom_levels(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test custom log levels from environment."""
        monkeypatch.setenv("LOG_LEVEL", "10")  # DEBUG
        monkeypatch.setenv("LOG_DISCORD_LEVEL", "40")  # ERROR
        monkeypatch.setenv("LOG_WEBSOCKETS_LEVEL", "50")  # CRITICAL
        monkeypatch.setenv("LOG_ASYNCIO_LEVEL", "30")  # WARNING
        monkeypatch.setenv("LOG_HTTP_CORE_LEVEL", "40")
        monkeypatch.setenv("LOG_HTTPX_LEVEL", "40")

        settings = LogSettings()

        assert settings.LEVEL == 10
        assert settings.DISCORD_LEVEL == 40
        assert settings.WEBSOCKETS_LEVEL == 50
        assert settings.ASYNCIO_LEVEL == 30
        assert settings.HTTP_CORE_LEVEL == 40
        assert settings.HTTPX_LEVEL == 40

    def test_log_settings_format_default(self) -> None:
        """Test default log format."""
        settings = LogSettings()

        assert "%(asctime)s" in settings.FORMAT
        assert "%(name)s" in settings.FORMAT
        assert "%(levelname)s" in settings.FORMAT
        assert "%(message)s" in settings.FORMAT

    def test_log_settings_custom_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test custom log format from environment."""
        custom_format = "%(levelname)s - %(message)s"
        monkeypatch.setenv("LOG_FORMAT", custom_format)

        settings = LogSettings()

        assert settings.FORMAT == custom_format

    def test_log_settings_file_path(self) -> None:
        """Test log file path is a Path object."""
        settings = LogSettings()

        assert isinstance(settings.FILE, Path)
        assert str(settings.FILE).endswith("byte.log")

    def test_log_settings_custom_file_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test custom log file path from environment."""
        custom_path = "/tmp/custom.log"
        monkeypatch.setenv("LOG_FILE", custom_path)

        settings = LogSettings()

        assert str(settings.FILE) == custom_path

    def test_log_settings_env_prefix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test LOG_ prefix is used for environment variables."""
        monkeypatch.setenv("LOG_LEVEL", "50")

        settings = LogSettings()

        assert settings.LEVEL == 50


class TestProjectSettings:
    """Tests for ProjectSettings."""

    def test_project_settings_defaults(self) -> None:
        """Test ProjectSettings has expected default types."""
        settings = ProjectSettings()

        # DEBUG and ENVIRONMENT come from .env, just verify types
        assert isinstance(settings.DEBUG, bool)
        assert isinstance(settings.ENVIRONMENT, str)
        assert isinstance(settings.VERSION, str)
        assert len(settings.VERSION) > 0

    def test_project_settings_debug_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test debug mode from environment."""
        monkeypatch.setenv("DEBUG", "true")

        settings = ProjectSettings()

        assert settings.DEBUG is True

    def test_project_settings_environment_dev(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test dev environment setting."""
        monkeypatch.setenv("ENVIRONMENT", "dev")

        settings = ProjectSettings()

        assert settings.ENVIRONMENT == "dev"

    def test_project_settings_environment_test(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test test environment setting."""
        monkeypatch.setenv("ENVIRONMENT", "test")

        settings = ProjectSettings()

        assert settings.ENVIRONMENT == "test"

    def test_project_settings_version_from_metadata(self) -> None:
        """Test version is loaded from __metadata__."""
        settings = ProjectSettings()

        # Version should be a valid semver string
        assert "." in settings.VERSION


class TestLoadSettings:
    """Tests for load_settings function."""

    def test_load_settings_returns_tuple(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test load_settings returns tuple of three settings objects."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "123")
        monkeypatch.setenv("DISCORD_DEV_USER_ID", "456")

        discord, log, project = load_settings()

        assert isinstance(discord, DiscordSettings)
        assert isinstance(log, LogSettings)
        assert isinstance(project, ProjectSettings)

    def test_load_settings_discord_token_exists(self) -> None:
        """Test Discord token is populated in loaded settings."""
        discord, _, _ = load_settings()

        # Token should be loaded from .env
        assert isinstance(discord.TOKEN, str)
        assert len(discord.TOKEN) > 0

    def test_load_settings_all_settings_have_values(self) -> None:
        """Test each settings object has values."""
        discord, log, project = load_settings()

        # Each should have its own settings
        assert isinstance(discord.TOKEN, str)
        assert isinstance(log.LEVEL, int)
        assert isinstance(project.ENVIRONMENT, str)
