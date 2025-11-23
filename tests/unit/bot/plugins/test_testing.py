"""Tests for testing plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest

from byte_bot.plugins.testing import TestCog, setup

if TYPE_CHECKING:
    from discord.ext.commands import Bot, Context


class TestTestingCog:
    """Tests for TestCog."""

    def test_test_cog_initialization(self, mock_bot: Bot) -> None:
        """Test TestCog initializes correctly."""
        cog = TestCog(mock_bot)

        assert cog.bot == mock_bot
        assert cog.__cog_name__ == "Testing Commands"

    @pytest.mark.asyncio
    async def test_testing_group_without_subcommand(self, mock_bot: Bot, mock_context: Context) -> None:
        """Test testing command group when no subcommand is provided."""
        cog = TestCog(mock_bot)

        # Mock context with no invoked subcommand
        mock_context.invoked_subcommand = None
        mock_context.subcommand_passed = "invalid"
        mock_context.command = cog.testing
        mock_context.send_help = AsyncMock()

        await cog.testing.callback(cog, mock_context)

        # Should send error message
        assert mock_context.send.call_count >= 1
        mock_context.send_help.assert_called_once()

    @pytest.mark.asyncio
    async def test_ping_command(self, mock_bot: Bot, mock_context: Context) -> None:
        """Test ping command responds with pong."""
        cog = TestCog(mock_bot)

        await cog.ping.callback(cog, mock_context)

        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0]
        assert "pong" in call_args[0].lower()

    @pytest.mark.asyncio
    async def test_setup_adds_cog_to_bot(self, mock_bot: Bot) -> None:
        """Test setup function adds TestCog to bot."""
        mock_bot.add_cog = AsyncMock()

        await setup(mock_bot)

        mock_bot.add_cog.assert_called_once()
        cog = mock_bot.add_cog.call_args[0][0]
        assert isinstance(cog, TestCog)
        assert cog.bot == mock_bot
