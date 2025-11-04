"""Tests for Discord bot core functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord import Activity, Intents

from byte_bot.byte.bot import Byte

if TYPE_CHECKING:
    pass

__all__ = (
    "TestBotEventHandlers",
    "TestByteBot",
)


class TestByteBot:
    """Test suite for Byte bot initialization and setup."""

    def test_bot_initialization(self) -> None:
        """Test that Byte bot can be initialized."""
        intents = Intents.default()
        activity = Activity(name="test", type=discord.ActivityType.playing)

        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        assert bot is not None
        assert bot.command_prefix == ["!"]
        assert bot.intents == intents

    @pytest.mark.asyncio
    async def test_bot_setup_hook(self) -> None:
        """Test bot setup hook."""
        intents = Intents.default()
        activity = Activity(name="test", type=discord.ActivityType.playing)
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        # Mock the load_cogs method and tree
        with patch.object(bot, "load_cogs", new=AsyncMock()) as mock_load_cogs:
            with patch.object(bot.tree, "copy_global_to"):
                with patch.object(bot.tree, "sync", new=AsyncMock()) as mock_sync:
                    await bot.setup_hook()

                    # Verify cogs were loaded and tree was synced
                    mock_load_cogs.assert_called_once()
                    mock_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_cogs(self) -> None:
        """Test loading bot cogs/plugins."""
        intents = Intents.default()
        activity = Activity(name="test", type=discord.ActivityType.playing)
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        # Mock load_extension
        bot.load_extension = AsyncMock()

        # Mock the plugins directory to return no files (to avoid loading real cogs)
        with patch("byte_bot.byte.lib.settings.discord.PLUGINS_DIRS", []):
            await bot.load_cogs()

        # In test environment with no plugins, load_extension should not be called
        # (or handle empty plugin directory gracefully)


class TestBotEventHandlers:
    """Test suite for Discord bot event handlers."""

    @pytest.mark.asyncio
    async def test_on_ready_event(self, mock_bot: AsyncMock) -> None:
        """Test on_ready event handler.

        Args:
            mock_bot: Mock Discord bot
        """
        intents = Intents.default()
        activity = Activity(name="test", type=discord.ActivityType.playing)
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        # Mock the user property
        mock_user = MagicMock()
        mock_user.name = "ByteBot"
        with patch.object(type(bot), "user", new_callable=lambda: mock_user):
            # Call on_ready
            await bot.on_ready()

            # Should complete without errors

    @pytest.mark.asyncio
    async def test_on_message_processes_commands(self, mock_discord_message: MagicMock) -> None:
        """Test that on_message processes commands.

        Args:
            mock_discord_message: Mock Discord message
        """
        intents = Intents.default()
        activity = Activity(name="test", type=discord.ActivityType.playing)
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        # Mock process_commands
        bot.process_commands = AsyncMock()

        await bot.on_message(mock_discord_message)

        bot.process_commands.assert_called_once_with(mock_discord_message)

    @pytest.mark.asyncio
    async def test_on_member_join(self, mock_discord_member: MagicMock) -> None:
        """Test member join event handler.

        Args:
            mock_discord_member: Mock Discord member
        """
        # Member join should send welcome message
        await Byte.on_member_join(mock_discord_member)

        # Verify send was called (for non-bot members)
        if not mock_discord_member.bot:
            mock_discord_member.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_member_join_ignores_bots(self, mock_discord_member: MagicMock) -> None:
        """Test that member join ignores bot accounts.

        Args:
            mock_discord_member: Mock Discord member
        """
        mock_discord_member.bot = True
        mock_discord_member.send.reset_mock()

        await Byte.on_member_join(mock_discord_member)

        # Should not send message to bots
        mock_discord_member.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_guild_join(self, mock_discord_guild: MagicMock) -> None:
        """Test guild join event handler.

        Args:
            mock_discord_guild: Mock Discord guild
        """
        intents = Intents.default()
        activity = Activity(name="test", type=discord.ActivityType.playing)
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        # Mock tree sync and get_guild
        with patch.object(bot.tree, "sync", new=AsyncMock()) as mock_sync:
            with patch.object(bot, "get_guild", return_value=None):
                # Mock httpx client to avoid real API calls
                with patch("httpx.AsyncClient") as mock_client:
                    mock_response = AsyncMock()
                    mock_response.status_code = 201
                    mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

                    await bot.on_guild_join(mock_discord_guild)

                    # Verify tree was synced for the guild
                    mock_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_command_error(self, mock_discord_message: MagicMock) -> None:
        """Test command error handler.

        Args:
            mock_discord_message: Mock Discord message
        """
        intents = Intents.default()
        activity = Activity(name="test", type=discord.ActivityType.playing)
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        # Create a mock context
        ctx = MagicMock()
        ctx.author = mock_discord_message.author
        ctx.message = mock_discord_message
        ctx.channel = mock_discord_message.channel
        ctx.guild = mock_discord_message.guild
        ctx.command = "test_command"
        ctx.send = AsyncMock()

        # Create a mock error
        from discord.ext.commands import CommandError

        error = CommandError("Test error")

        await bot.on_command_error(ctx, error)

        # Verify error message was sent
        ctx.send.assert_called_once()
