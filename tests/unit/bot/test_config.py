"""Tests for bot configuration loading."""

from __future__ import annotations

import pytest


class TestBotSettings:
    """Tests for BotSettings class."""

    def test_bot_settings_loads_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that BotSettings loads from environment variables."""
        from byte_bot.config import BotSettings

        # Set up environment variables
        monkeypatch.setenv("DISCORD_TOKEN", "test-token-123")
        monkeypatch.setenv("DISCORD_DEV_GUILD_ID", "987654321")
        monkeypatch.setenv("API_SERVICE_URL", "http://test-api:9000")
        monkeypatch.setenv("ENVIRONMENT", "test")

        # Load settings
        settings = BotSettings()

        # Verify settings loaded correctly
        assert settings.discord_token == "test-token-123"
        assert settings.discord_dev_guild_id == 987654321
        assert settings.api_service_url == "http://test-api:9000"
        assert settings.environment == "test"

    def test_command_prefix_assembly(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test command prefix assembly based on environment."""
        from byte_bot.config import BotSettings

        monkeypatch.setenv("DISCORD_TOKEN", "test-token")
        monkeypatch.setenv("ENVIRONMENT", "dev")

        settings = BotSettings()

        # Dev environment should have "nibble " prefix
        assert "nibble " in settings.command_prefix

    def test_presence_url_assembly(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test presence URL assembly based on environment."""
        from byte_bot.config import BotSettings

        monkeypatch.setenv("DISCORD_TOKEN", "test-token")
        monkeypatch.setenv("ENVIRONMENT", "dev")

        settings = BotSettings()

        # Dev environment should use dev URL
        assert "dev.byte-bot.app" in settings.presence_url


class TestLogSettings:
    """Tests for LogSettings class."""

    def test_log_settings_has_defaults(self) -> None:
        """Test that LogSettings has reasonable default values."""
        from byte_bot.config import LogSettings

        settings = LogSettings()

        # Should have default values (may be from env or defaults)
        assert isinstance(settings.level, int)
        assert isinstance(settings.discord_level, int)
        assert isinstance(settings.websockets_level, int)
        assert isinstance(settings.asyncio_level, int)
        assert isinstance(settings.httpx_level, int)


class TestLoadSettings:
    """Tests for load_settings function."""

    def test_load_settings_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test successful settings loading."""
        from byte_bot.config import load_settings

        monkeypatch.setenv("DISCORD_TOKEN", "test-token")

        # Reimport to avoid cached module-level settings
        from importlib import reload

        import byte_bot.config

        reload(byte_bot.config)
        from byte_bot.config import BotSettings, LogSettings

        bot_settings, log_settings = load_settings()

        assert isinstance(bot_settings, BotSettings)
        assert isinstance(log_settings, LogSettings)
        assert bot_settings.discord_token

    def test_load_settings_returns_tuple(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that load_settings returns a tuple of settings."""
        from byte_bot.config import load_settings

        monkeypatch.setenv("DISCORD_TOKEN", "test-token")

        from importlib import reload

        import byte_bot.config

        reload(byte_bot.config)
        from byte_bot.config import BotSettings, LogSettings

        bot_settings, log_settings = load_settings()

        assert isinstance(bot_settings, BotSettings)
        assert isinstance(log_settings, LogSettings)
