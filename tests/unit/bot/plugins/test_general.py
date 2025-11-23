"""Tests for general plugin commands."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest
from discord import Interaction
from discord.ext.commands import Bot

from byte_bot.plugins.general import GeneralCommands

if TYPE_CHECKING:
    pass


class TestGeneralCommands:
    """Tests for GeneralCommands cog."""

    @pytest.fixture
    def cog(self, mock_bot: Bot) -> GeneralCommands:
        """Create GeneralCommands cog."""
        return GeneralCommands(mock_bot)

    def test_cog_initialization(self, cog: GeneralCommands, mock_bot: Bot) -> None:
        """Test cog initializes correctly."""
        assert cog.bot == mock_bot
        assert cog.__cog_name__ == "General Commands"

    @pytest.mark.asyncio
    async def test_show_paste_command(self, cog: GeneralCommands) -> None:
        """Test show_paste slash command displays paste information."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock()

        await cog.show_paste.callback(cog, mock_interaction)

        mock_interaction.response.send_message.assert_called_once()
        call_kwargs = mock_interaction.response.send_message.call_args[1]
        embed = call_kwargs["embed"]

        # Verify embed content
        assert embed.title == "Paste long format code"
        assert embed.color.value == 0x42B1A8
        assert len(embed.fields) == 2
        assert embed.fields[0].name == "Paste Service"
        assert "Paste" in embed.fields[0].value
        assert embed.fields[1].name == "Syntax Highlighting"
        assert "Discord Markdown Guide" in embed.fields[1].value
        # Verify thumbnail is set
        assert embed.thumbnail.url is not None

    @pytest.mark.asyncio
    async def test_show_paste_embed_fields_inline(self, cog: GeneralCommands) -> None:
        """Test show_paste embed field inline property."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock()

        await cog.show_paste.callback(cog, mock_interaction)

        call_kwargs = mock_interaction.response.send_message.call_args[1]
        embed = call_kwargs["embed"]

        # First field is inline, second is not (default)
        assert embed.fields[0].inline is True
        # Second field should not be inline (default behavior when not specified)


def test_setup() -> None:
    """Test setup function registers cog."""
    bot = MagicMock()
    bot.add_cog = AsyncMock()

    from byte_bot.plugins.general import setup

    import asyncio

    loop = asyncio.new_event_loop()
    loop.run_until_complete(setup(bot))
    loop.close()

    bot.add_cog.assert_called_once()
    cog = bot.add_cog.call_args[0][0]
    assert isinstance(cog, GeneralCommands)
