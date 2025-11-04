"""Tests for Discord bot plugins/commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass

__all__ = (
    "TestAdminPlugin",
    "TestGeneralPlugin",
)


class TestAdminPlugin:
    """Test suite for admin plugin commands."""

    @pytest.mark.asyncio
    async def test_admin_plugin_loads(self) -> None:
        """Test that admin plugin can be loaded."""
        # This is a basic test to verify the plugin file structure
        try:
            from byte_bot.byte.plugins import admin

            assert admin is not None
        except ImportError as e:
            pytest.fail(f"Failed to import admin plugin: {e}")

    @pytest.mark.asyncio
    async def test_admin_commands_exist(self) -> None:
        """Test that admin plugin has expected commands."""
        from byte_bot.byte.plugins import admin

        # Check if plugin has setup function (standard for discord.py cogs)
        assert hasattr(admin, "setup")


class TestGeneralPlugin:
    """Test suite for general plugin commands."""

    @pytest.mark.asyncio
    async def test_general_plugin_loads(self) -> None:
        """Test that general plugin can be loaded."""
        try:
            from byte_bot.byte.plugins import general

            assert general is not None
        except ImportError as e:
            pytest.fail(f"Failed to import general plugin: {e}")

    @pytest.mark.asyncio
    async def test_general_commands_exist(self) -> None:
        """Test that general plugin has expected commands."""
        from byte_bot.byte.plugins import general

        assert hasattr(general, "setup")


class TestGitHubPlugin:
    """Test suite for GitHub plugin commands."""

    @pytest.mark.asyncio
    async def test_github_plugin_loads(self) -> None:
        """Test that GitHub plugin can be loaded."""
        try:
            from byte_bot.byte.plugins import github

            assert github is not None
        except ImportError as e:
            pytest.fail(f"Failed to import github plugin: {e}")


class TestConfigPlugin:
    """Test suite for config plugin commands."""

    @pytest.mark.asyncio
    async def test_config_plugin_loads(self) -> None:
        """Test that config plugin can be loaded."""
        try:
            from byte_bot.byte.plugins import config

            assert config is not None
        except ImportError as e:
            pytest.fail(f"Failed to import config plugin: {e}")


class TestForumsPlugin:
    """Test suite for forums plugin commands."""

    @pytest.mark.asyncio
    async def test_forums_plugin_loads(self) -> None:
        """Test that forums plugin can be loaded."""
        try:
            from byte_bot.byte.plugins import forums

            assert forums is not None
        except ImportError as e:
            pytest.fail(f"Failed to import forums plugin: {e}")
