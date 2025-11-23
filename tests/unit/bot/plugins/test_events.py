"""Tests for events plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from byte_bot.plugins.events import Events, setup

if TYPE_CHECKING:
    from discord.ext.commands import Bot


class TestEventsCog:
    """Tests for Events cog."""

    def test_events_cog_initialization(self, mock_bot: Bot) -> None:
        """Test Events cog initializes correctly."""
        cog = Events(mock_bot)

        assert cog.bot == mock_bot

    @pytest.mark.asyncio
    async def test_on_thread_create_help_forum(self, mock_bot: Bot) -> None:
        """Test on_thread_create for help forum thread."""
        cog = Events(mock_bot)

        # Mock thread
        mock_thread = MagicMock()
        mock_thread.name = "Test Thread"
        mock_thread.parent = MagicMock()
        mock_thread.parent.name = "help"
        mock_thread.owner = MagicMock()
        mock_thread.owner.mention = "<@123>"
        mock_thread.guild = MagicMock()
        mock_thread.guild.id = 555555555
        mock_thread.send = AsyncMock()

        # Mock HelpThreadView
        with patch("byte_bot.plugins.events.HelpThreadView") as mock_view_cls:
            mock_view = MagicMock()
            mock_view.setup = AsyncMock()
            mock_view_cls.return_value = mock_view

            await cog.on_thread_create(mock_thread)

            # Verify setup was called
            mock_view.setup.assert_called_once()
            # Verify send was called with embed and view
            mock_thread.send.assert_called_once()
            call_kwargs = mock_thread.send.call_args[1]
            assert "embed" in call_kwargs
            assert "view" in call_kwargs

    @pytest.mark.asyncio
    async def test_on_thread_create_help_forum_no_owner(self, mock_bot: Bot) -> None:
        """Test on_thread_create for help forum without owner."""
        cog = Events(mock_bot)

        # Mock thread without owner
        mock_thread = MagicMock()
        mock_thread.name = "Test Thread"
        mock_thread.parent = MagicMock()
        mock_thread.parent.name = "help"
        mock_thread.owner = None
        mock_thread.send = AsyncMock()

        await cog.on_thread_create(mock_thread)

        # Should not send message without owner
        mock_thread.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_thread_create_general_forum(self, mock_bot: Bot) -> None:
        """Test on_thread_create for general forum thread."""
        cog = Events(mock_bot)

        # Mock thread
        mock_thread = MagicMock()
        mock_thread.name = "General Discussion"
        mock_thread.parent = MagicMock()
        mock_thread.parent.name = "forum"
        mock_thread.owner = MagicMock()
        mock_thread.owner.mention = "<@456>"
        mock_thread.send = AsyncMock()

        await cog.on_thread_create(mock_thread)

        # Verify send was called with welcome message
        mock_thread.send.assert_called_once()
        call_args = mock_thread.send.call_args[0]
        assert "Thanks for posting" in call_args[0]
        assert "<@456>" in call_args[0]

    @pytest.mark.asyncio
    async def test_on_thread_create_general_forum_no_owner(self, mock_bot: Bot) -> None:
        """Test on_thread_create for general forum without owner."""
        cog = Events(mock_bot)

        # Mock thread without owner
        mock_thread = MagicMock()
        mock_thread.name = "General Discussion"
        mock_thread.parent = MagicMock()
        mock_thread.parent.name = "forum"
        mock_thread.owner = None
        mock_thread.send = AsyncMock()

        await cog.on_thread_create(mock_thread)

        # Should not send message without owner
        mock_thread.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_thread_create_other_forum(self, mock_bot: Bot) -> None:
        """Test on_thread_create for non-help/forum thread."""
        cog = Events(mock_bot)

        # Mock thread in different forum
        mock_thread = MagicMock()
        mock_thread.name = "Off Topic"
        mock_thread.parent = MagicMock()
        mock_thread.parent.name = "random"
        mock_thread.owner = MagicMock()
        mock_thread.send = AsyncMock()

        await cog.on_thread_create(mock_thread)

        # Should not send any message
        mock_thread.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_thread_create_no_parent(self, mock_bot: Bot) -> None:
        """Test on_thread_create for thread without parent."""
        cog = Events(mock_bot)

        # Mock thread without parent
        mock_thread = MagicMock()
        mock_thread.name = "Orphan Thread"
        mock_thread.parent = None
        mock_thread.send = AsyncMock()

        await cog.on_thread_create(mock_thread)

        # Should not send any message
        mock_thread.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_setup_adds_cog_to_bot(self, mock_bot: Bot) -> None:
        """Test setup function adds Events cog to bot."""
        mock_bot.add_cog = AsyncMock()

        await setup(mock_bot)

        mock_bot.add_cog.assert_called_once()
        cog = mock_bot.add_cog.call_args[0][0]
        assert isinstance(cog, Events)
        assert cog.bot == mock_bot
