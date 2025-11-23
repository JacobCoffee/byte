"""Tests for admin plugin commands."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from discord import Interaction
from discord.ext.commands import Bot, Context, ExtensionNotFound, ExtensionNotLoaded
from httpx import ConnectError

from byte_bot.plugins.admin import AdminCommands

if TYPE_CHECKING:
    pass


class TestAdminCommands:
    """Tests for AdminCommands cog."""

    @pytest.fixture
    def bot(self, mock_bot: Bot) -> Bot:
        """Create mock bot."""
        mock_bot.extensions = {
            "byte_bot.plugins.admin": MagicMock(),
            "byte_bot.plugins.general": MagicMock(),
            "byte_bot.plugins.github": MagicMock(),
        }
        mock_bot.reload_extension = AsyncMock()
        mock_bot.tree.sync = AsyncMock(return_value=[])
        return mock_bot

    @pytest.fixture
    def cog(self, bot: Bot) -> AdminCommands:
        """Create AdminCommands cog."""
        return AdminCommands(bot)

    def test_cog_initialization(self, cog: AdminCommands, bot: Bot) -> None:
        """Test cog initializes correctly."""
        assert cog.bot == bot
        assert cog.__cog_name__ == "Admin Commands"

    async def test_admin_group_no_subcommand(self, cog: AdminCommands, mock_context: Context) -> None:
        """Test admin group command with no subcommand."""
        mock_context.invoked_subcommand = None
        mock_context.send = AsyncMock()
        mock_context.send_help = AsyncMock()
        mock_context.command = MagicMock()

        # Call the underlying method directly
        await cog.admin.callback(cog, mock_context)

        # Updated expectation: admin method only sends one message now
        mock_context.send.assert_called_once()
        mock_context.send_help.assert_called_once()

    async def test_list_cogs(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test list_cogs command."""
        mock_context.send = AsyncMock()

        # Call the underlying method directly
        await cog.list_cogs.callback(cog, mock_context)

        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "admin" in call_args
        assert "general" in call_args
        assert "github" in call_args

    async def test_reload_single_cog_success(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test reloading single cog successfully."""
        mock_context.send = AsyncMock()
        bot.reload_extension = AsyncMock()

        # Call the underlying method directly
        await cog.reload.callback(cog, mock_context, "admin")

        bot.reload_extension.assert_called_once_with("byte_bot.plugins.admin")
        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "reloaded" in call_args.lower()

    async def test_reload_single_cog_not_found(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test reloading non-existent cog."""
        mock_context.send = AsyncMock()
        bot.reload_extension = AsyncMock(side_effect=ExtensionNotFound("test"))

        # Call the underlying method directly
        await cog.reload.callback(cog, mock_context, "nonexistent")

        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "Error" in call_args

    async def test_reload_single_cog_not_loaded(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test reloading cog that's not loaded."""
        mock_context.send = AsyncMock()
        bot.reload_extension = AsyncMock(side_effect=ExtensionNotLoaded("test"))

        # Call the underlying method directly
        await cog.reload.callback(cog, mock_context, "unloaded")

        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "Error" in call_args

    async def test_reload_all_cogs(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test reloading all cogs."""
        mock_context.send = AsyncMock()
        bot.reload_extension = AsyncMock()

        # Call the underlying method directly
        await cog.reload.callback(cog, mock_context, "all")

        # Should reload all 3 extensions
        assert bot.reload_extension.call_count == 3
        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "All cogs reloaded" in call_args

    async def test_reload_all_cogs_with_failures(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test reloading all cogs with some failures."""
        mock_context.send = AsyncMock()

        # First two succeed, third fails
        bot.reload_extension = AsyncMock(side_effect=[None, None, ExtensionNotFound("test")])

        # Call the underlying method directly
        await cog.reload.callback(cog, mock_context, "all")

        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "Error" in call_args
        assert "All cogs reloaded" in call_args

    async def test_tree_sync(self, cog: AdminCommands, bot: Bot) -> None:
        """Test tree sync slash command."""
        interaction = MagicMock(spec=Interaction)
        interaction.response.send_message = AsyncMock()

        # Mock sync results with proper name attribute
        mock_cmd1 = MagicMock()
        mock_cmd1.name = "command1"
        mock_cmd2 = MagicMock()
        mock_cmd2.name = "command2"
        sync_result = [mock_cmd1, mock_cmd2]
        bot.tree.sync = AsyncMock(return_value=sync_result)

        # Call the underlying method directly (tree_sync is an app_command)
        await cog.tree_sync.callback(cog, interaction)

        bot.tree.sync.assert_called_once()
        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs["ephemeral"] is True

    async def test_bootstrap_guild_uses_context_guild(
        self, cog: AdminCommands, mock_context: Context, bot: Bot
    ) -> None:
        """Test bootstrap_guild uses context guild if no ID provided."""
        mock_context.send = AsyncMock()

        # Create a mock guild and configure bot to return it
        mock_guild = MagicMock()
        mock_guild.id = 123456789
        mock_guild.name = "Test Guild"
        mock_context.guild = mock_guild
        bot.get_guild = MagicMock(return_value=mock_guild)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with patch("byte_bot.plugins.admin.bot_settings") as mock_settings:
                mock_settings.api_service_url = "http://localhost:8000"
                # Call the underlying method directly
                await cog.bootstrap_guild.callback(cog, mock_context, guild_id=None)

            call_args = mock_client.post.call_args[0][0]
            assert "123456789" in call_args
            assert "Test Guild" in call_args

    async def test_bootstrap_guild_with_explicit_id(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test bootstrap_guild with explicit guild ID."""
        mock_context.send = AsyncMock()
        mock_guild = MagicMock()
        mock_guild.id = 999999999
        mock_guild.name = "Custom Guild"
        bot.get_guild = MagicMock(return_value=mock_guild)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with patch("byte_bot.plugins.admin.bot_settings") as mock_settings:
                mock_settings.api_service_url = "http://localhost:8000"
                # Call the underlying method directly
                await cog.bootstrap_guild.callback(cog, mock_context, guild_id=999999999)

            call_args = mock_client.post.call_args[0][0]
            assert "999999999" in call_args


def test_setup():
    """Test setup function registers cog."""
    bot = MagicMock()
    bot.add_cog = AsyncMock()

    # Call setup synchronously (it should be async but we're just checking registration)
    # In reality, setup is called by discord.py's extension loader
    import asyncio

    from byte_bot.plugins.admin import setup

    asyncio.run(setup(bot))

    bot.add_cog.assert_called_once()


class TestAdminCommandsEdgeCases:
    """Edge case tests for AdminCommands cog."""

    @pytest.fixture
    def bot(self, mock_bot: Bot) -> Bot:
        """Create mock bot."""
        mock_bot.extensions = {
            "byte_bot.plugins.admin": MagicMock(),
            "byte_bot.plugins.general": MagicMock(),
            "byte_bot.plugins.github": MagicMock(),
        }
        mock_bot.reload_extension = AsyncMock()
        mock_bot.tree.sync = AsyncMock(return_value=[])
        return mock_bot

    @pytest.fixture
    def cog(self, bot: Bot) -> AdminCommands:
        """Create AdminCommands cog."""
        return AdminCommands(bot)

    async def test_reload_with_empty_extension_name(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test reloading with empty extension name."""
        mock_context.send = AsyncMock()
        bot.reload_extension = AsyncMock(side_effect=ExtensionNotFound(""))

        await cog.reload.callback(cog, mock_context, "")

        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "Error" in call_args

    async def test_reload_all_with_no_extensions(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test reloading all when no extensions loaded."""
        mock_context.send = AsyncMock()
        bot.extensions = {}

        await cog.reload.callback(cog, mock_context, "all")

        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "All cogs reloaded" in call_args

    async def test_reload_all_with_all_failures(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test reloading all cogs when all fail."""
        mock_context.send = AsyncMock()
        bot.reload_extension = AsyncMock(side_effect=ExtensionNotFound("All failed"))

        await cog.reload.callback(cog, mock_context, "all")

        mock_context.send.assert_called_once()
        # Should contain error messages but still report completion
        call_args = mock_context.send.call_args[0][0]
        assert "Error" in call_args

    async def test_tree_sync_with_empty_results(self, cog: AdminCommands, bot: Bot) -> None:
        """Test tree sync when no commands synced."""
        interaction = MagicMock(spec=Interaction)
        interaction.response.send_message = AsyncMock()
        bot.tree.sync = AsyncMock(return_value=[])

        await cog.tree_sync.callback(cog, interaction)

        bot.tree.sync.assert_called_once()
        interaction.response.send_message.assert_called_once()

    async def test_tree_sync_failure(self, cog: AdminCommands, bot: Bot) -> None:
        """Test tree sync when sync fails."""
        interaction = MagicMock(spec=Interaction)
        interaction.response.send_message = AsyncMock()
        bot.tree.sync = AsyncMock(side_effect=Exception("Sync failed"))

        with pytest.raises(Exception, match="Sync failed"):
            await cog.tree_sync.callback(cog, interaction)

    async def test_bootstrap_guild_no_guild_context(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test bootstrap_guild when not in guild context and no ID provided."""
        mock_context.send = AsyncMock()
        mock_context.guild = None

        await cog.bootstrap_guild.callback(cog, mock_context, guild_id=None)

        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "No guild ID" in call_args or "not used in a guild" in call_args

    async def test_bootstrap_guild_bot_not_in_guild(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test bootstrap_guild when bot is not in specified guild."""
        mock_context.send = AsyncMock()
        bot.get_guild = MagicMock(return_value=None)

        await cog.bootstrap_guild.callback(cog, mock_context, guild_id=999999999)

        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "Bot is not in guild" in call_args or "not in guild" in call_args.lower()

    async def test_bootstrap_guild_api_connection_error(
        self, cog: AdminCommands, mock_context: Context, bot: Bot
    ) -> None:
        """Test bootstrap_guild when API connection fails."""
        mock_context.send = AsyncMock()
        mock_guild = MagicMock()
        mock_guild.id = 123456789
        mock_guild.name = "Test Guild"
        bot.get_guild = MagicMock(return_value=mock_guild)
        bot.tree.sync = AsyncMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.post = AsyncMock(side_effect=ConnectError("Connection failed"))
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with patch("byte_bot.plugins.admin.bot_settings") as mock_settings:
                mock_settings.api_service_url = "http://localhost:8000"
                await cog.bootstrap_guild.callback(cog, mock_context, guild_id=None)

            # Should send error message
            assert mock_context.send.call_count >= 2  # Initial message + error

    async def test_bootstrap_guild_api_conflict(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test bootstrap_guild when guild already exists."""
        mock_context.send = AsyncMock()
        mock_guild = MagicMock()
        mock_guild.id = 123456789
        mock_guild.name = "Test Guild"
        bot.get_guild = MagicMock(return_value=mock_guild)
        bot.tree.sync = AsyncMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 409  # Conflict
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with patch("byte_bot.plugins.admin.bot_settings") as mock_settings:
                mock_settings.api_service_url = "http://localhost:8000"
                await cog.bootstrap_guild.callback(cog, mock_context, guild_id=None)

            # Should send conflict message
            calls = [str(call) for call in mock_context.send.call_args_list]
            assert any("already exists" in str(call).lower() for call in calls)

    async def test_bootstrap_guild_api_unexpected_status(
        self, cog: AdminCommands, mock_context: Context, bot: Bot
    ) -> None:
        """Test bootstrap_guild with unexpected API status code."""
        mock_context.send = AsyncMock()
        mock_guild = MagicMock()
        mock_guild.id = 123456789
        mock_guild.name = "Test Guild"
        bot.get_guild = MagicMock(return_value=mock_guild)
        bot.tree.sync = AsyncMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 500  # Server error
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with patch("byte_bot.plugins.admin.bot_settings") as mock_settings:
                mock_settings.api_service_url = "http://localhost:8000"
                await cog.bootstrap_guild.callback(cog, mock_context, guild_id=None)

            # Should send error message
            calls = [str(call) for call in mock_context.send.call_args_list]
            assert any("failed" in str(call).lower() for call in calls)

    async def test_bootstrap_guild_command_sync_failure(
        self, cog: AdminCommands, mock_context: Context, bot: Bot
    ) -> None:
        """Test bootstrap_guild when command sync fails."""
        mock_context.send = AsyncMock()
        mock_guild = MagicMock()
        mock_guild.id = 123456789
        mock_guild.name = "Test Guild"
        bot.get_guild = MagicMock(return_value=mock_guild)
        bot.tree.sync = AsyncMock(side_effect=Exception("Sync error"))

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with patch("byte_bot.plugins.admin.bot_settings") as mock_settings:
                mock_settings.api_service_url = "http://localhost:8000"
                # Should not raise, just log the error
                await cog.bootstrap_guild.callback(cog, mock_context, guild_id=None)

    async def test_list_cogs_empty(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test list_cogs when no cogs are loaded."""
        mock_context.send = AsyncMock()
        bot.extensions = {}

        await cog.list_cogs.callback(cog, mock_context)

        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "Loaded cogs:" in call_args

    async def test_reload_with_generic_exception(self, cog: AdminCommands, mock_context: Context, bot: Bot) -> None:
        """Test reload handles unexpected exceptions."""
        mock_context.send = AsyncMock()
        bot.reload_extension = AsyncMock(side_effect=RuntimeError("Unexpected error"))

        # Should not catch generic exceptions, let them propagate
        with pytest.raises(RuntimeError, match="Unexpected error"):
            await cog.reload.callback(cog, mock_context, "admin")
