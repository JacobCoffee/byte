"""Tests for Discord bot views and UI components."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass

__all__ = (
    "TestBotViews",
    "TestViewComponents",
)


class TestBotViews:
    """Test suite for Discord UI views."""

    @pytest.mark.asyncio
    async def test_views_module_loads(self) -> None:
        """Test that views module can be loaded."""
        try:
            from byte_bot.byte import views

            assert views is not None
        except ImportError as e:
            pytest.fail(f"Failed to import views module: {e}")

    @pytest.mark.asyncio
    async def test_abstract_views_load(self) -> None:
        """Test that abstract views can be loaded."""
        try:
            from byte_bot.byte.views import abstract_views

            assert abstract_views is not None
        except ImportError as e:
            pytest.fail(f"Failed to import abstract_views: {e}")


class TestViewComponents:
    """Test suite for specific view components."""

    @pytest.mark.asyncio
    async def test_config_views_load(self) -> None:
        """Test that config views can be loaded."""
        try:
            from byte_bot.byte.views import config

            assert config is not None
        except ImportError as e:
            pytest.fail(f"Failed to import config views: {e}")

    @pytest.mark.asyncio
    async def test_python_views_load(self) -> None:
        """Test that python views can be loaded."""
        try:
            from byte_bot.byte.views import python

            assert python is not None
        except ImportError as e:
            pytest.fail(f"Failed to import python views: {e}")

    @pytest.mark.asyncio
    async def test_forums_views_load(self) -> None:
        """Test that forums views can be loaded."""
        try:
            from byte_bot.byte.views import forums

            assert forums is not None
        except ImportError as e:
            pytest.fail(f"Failed to import forums views: {e}")
