"""Tests for log module."""

from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import patch

from byte_bot.lib.log import get_logger, setup_logging


class TestLogging:
    """Tests for logging utilities."""

    def test_get_logger_default(self) -> None:
        """Test get_logger with default name."""
        logger = get_logger()

        assert isinstance(logger, logging.Logger)
        assert logger.name == "__main__"

    def test_get_logger_custom_name(self) -> None:
        """Test get_logger with custom name."""
        logger = get_logger("test_logger")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_setup_logging_creates_log_directory(self, tmp_path: Path) -> None:
        """Test setup_logging creates log directory if it doesn't exist."""
        log_file = tmp_path / "new_logs" / "byte.log"

        with (
            patch("byte_bot.lib.log.log_settings") as mock_log_settings,
            patch("byte_bot.lib.log.bot_settings") as mock_bot_settings,
        ):
            mock_log_settings.file = log_file
            mock_log_settings.format = "%(message)s"
            mock_log_settings.discord_level = 30
            mock_log_settings.websockets_level = 30
            mock_log_settings.asyncio_level = 20
            mock_log_settings.httpx_level = 30
            mock_bot_settings.environment = "dev"
            mock_bot_settings.debug = True

            setup_logging()

            # Verify directory was created
            assert log_file.parent.exists()

    def test_setup_logging_dev_environment(self) -> None:
        """Test setup_logging for dev environment uses RichHandler."""
        with (
            patch("byte_bot.lib.log.log_settings") as mock_log_settings,
            patch("byte_bot.lib.log.bot_settings") as mock_bot_settings,
            patch("logging.config.dictConfig") as mock_dictconfig,
        ):
            mock_log_settings.file = Path("/tmp/byte.log")
            mock_log_settings.format = "%(message)s"
            mock_log_settings.discord_level = 30
            mock_log_settings.websockets_level = 30
            mock_log_settings.asyncio_level = 20
            mock_log_settings.httpx_level = 30
            mock_bot_settings.environment = "dev"
            mock_bot_settings.debug = True

            setup_logging()

            # Verify dictConfig was called
            mock_dictconfig.assert_called_once()
            config = mock_dictconfig.call_args[0][0]

            # Check dev environment uses RichHandler for console
            assert config["handlers"]["console"]["class"] == "rich.logging.RichHandler"

    def test_setup_logging_prod_environment(self) -> None:
        """Test setup_logging for prod environment uses StreamHandler."""
        with (
            patch("byte_bot.lib.log.log_settings") as mock_log_settings,
            patch("byte_bot.lib.log.bot_settings") as mock_bot_settings,
            patch("logging.config.dictConfig") as mock_dictconfig,
        ):
            mock_log_settings.file = Path("/tmp/byte.log")
            mock_log_settings.format = "%(message)s"
            mock_log_settings.discord_level = 30
            mock_log_settings.websockets_level = 30
            mock_log_settings.asyncio_level = 20
            mock_log_settings.httpx_level = 30
            mock_bot_settings.environment = "prod"
            mock_bot_settings.debug = False

            setup_logging()

            mock_dictconfig.assert_called_once()
            config = mock_dictconfig.call_args[0][0]

            # Check prod environment uses StreamHandler for console
            assert config["handlers"]["console"]["class"] == "logging.StreamHandler"

    def test_setup_logging_configures_all_loggers(self) -> None:
        """Test setup_logging configures all expected loggers."""
        with (
            patch("byte_bot.lib.log.log_settings") as mock_log_settings,
            patch("byte_bot.lib.log.bot_settings") as mock_bot_settings,
            patch("logging.config.dictConfig") as mock_dictconfig,
        ):
            mock_log_settings.file = Path("/tmp/byte.log")
            mock_log_settings.format = "%(message)s"
            mock_log_settings.discord_level = 30
            mock_log_settings.websockets_level = 30
            mock_log_settings.asyncio_level = 20
            mock_log_settings.httpx_level = 30
            mock_bot_settings.environment = "dev"
            mock_bot_settings.debug = True

            setup_logging()

            config = mock_dictconfig.call_args[0][0]

            # Check all expected loggers are configured
            assert "discord" in config["loggers"]
            assert "httpcore" in config["loggers"]
            assert "httpx" in config["loggers"]
            assert "websockets" in config["loggers"]
            assert "asyncio" in config["loggers"]
            assert "root" in config["loggers"]
