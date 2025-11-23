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

    import asyncio

    from byte_bot.plugins.general import setup

    loop = asyncio.new_event_loop()
    loop.run_until_complete(setup(bot))
    loop.close()

    bot.add_cog.assert_called_once()
    cog = bot.add_cog.call_args[0][0]
    assert isinstance(cog, GeneralCommands)


class TestGeneralCommandsEdgeCases:
    """Edge case tests for GeneralCommands cog."""

    @pytest.fixture
    def cog(self, mock_bot: Bot) -> GeneralCommands:
        """Create GeneralCommands cog."""
        return GeneralCommands(mock_bot)

    @pytest.mark.asyncio
    async def test_show_paste_embed_color(self, cog: GeneralCommands) -> None:
        """Test show_paste embed has correct color."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock()

        await cog.show_paste.callback(cog, mock_interaction)

        call_kwargs = mock_interaction.response.send_message.call_args[1]
        embed = call_kwargs["embed"]

        # Verify specific color value (0x42B1A8)
        assert embed.color.value == 0x42B1A8

    @pytest.mark.asyncio
    async def test_show_paste_embed_title(self, cog: GeneralCommands) -> None:
        """Test show_paste embed has correct title."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock()

        await cog.show_paste.callback(cog, mock_interaction)

        call_kwargs = mock_interaction.response.send_message.call_args[1]
        embed = call_kwargs["embed"]

        assert embed.title == "Paste long format code"

    @pytest.mark.asyncio
    async def test_show_paste_embed_has_thumbnail(self, cog: GeneralCommands) -> None:
        """Test show_paste embed includes a thumbnail."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock()

        await cog.show_paste.callback(cog, mock_interaction)

        call_kwargs = mock_interaction.response.send_message.call_args[1]
        embed = call_kwargs["embed"]

        assert embed.thumbnail is not None
        assert embed.thumbnail.url is not None

    @pytest.mark.asyncio
    async def test_show_paste_embed_field_count(self, cog: GeneralCommands) -> None:
        """Test show_paste embed has exactly 2 fields."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock()

        await cog.show_paste.callback(cog, mock_interaction)

        call_kwargs = mock_interaction.response.send_message.call_args[1]
        embed = call_kwargs["embed"]

        assert len(embed.fields) == 2

    @pytest.mark.asyncio
    async def test_show_paste_first_field_is_inline(self, cog: GeneralCommands) -> None:
        """Test show_paste first field is inline."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock()

        await cog.show_paste.callback(cog, mock_interaction)

        call_kwargs = mock_interaction.response.send_message.call_args[1]
        embed = call_kwargs["embed"]

        assert embed.fields[0].inline is True

    @pytest.mark.asyncio
    async def test_show_paste_field_names(self, cog: GeneralCommands) -> None:
        """Test show_paste field names are correct."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock()

        await cog.show_paste.callback(cog, mock_interaction)

        call_kwargs = mock_interaction.response.send_message.call_args[1]
        embed = call_kwargs["embed"]

        assert embed.fields[0].name == "Paste Service"
        assert embed.fields[1].name == "Syntax Highlighting"

    @pytest.mark.asyncio
    async def test_show_paste_field_values_have_content(self, cog: GeneralCommands) -> None:
        """Test show_paste field values are not empty."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock()

        await cog.show_paste.callback(cog, mock_interaction)

        call_kwargs = mock_interaction.response.send_message.call_args[1]
        embed = call_kwargs["embed"]

        assert len(embed.fields[0].value) > 0
        assert len(embed.fields[1].value) > 0
        assert "Paste" in embed.fields[0].value
        assert "Discord Markdown Guide" in embed.fields[1].value

    @pytest.mark.asyncio
    async def test_show_paste_send_message_failure(self, cog: GeneralCommands) -> None:
        """Test show_paste handles send_message failure."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock(side_effect=Exception("Send failed"))

        with pytest.raises(Exception, match="Send failed"):
            await cog.show_paste.callback(cog, mock_interaction)

    @pytest.mark.asyncio
    async def test_show_paste_embed_is_not_ephemeral(self, cog: GeneralCommands) -> None:
        """Test show_paste response is not ephemeral (public)."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock()

        await cog.show_paste.callback(cog, mock_interaction)

        call_kwargs = mock_interaction.response.send_message.call_args[1]
        # Should not have ephemeral=True (or should be False)
        assert call_kwargs.get("ephemeral", False) is False

    def test_cog_name_attribute(self, cog: GeneralCommands, mock_bot: Bot) -> None:
        """Test GeneralCommands has correct cog name."""
        assert cog.__cog_name__ == "General Commands"

    def test_cog_bot_reference(self, cog: GeneralCommands, mock_bot: Bot) -> None:
        """Test GeneralCommands maintains reference to bot."""
        assert cog.bot == mock_bot

    @pytest.mark.asyncio
    async def test_show_paste_command_attributes(self, cog: GeneralCommands) -> None:
        """Test show_paste command has correct attributes."""
        assert hasattr(cog, "show_paste")
        assert hasattr(cog.show_paste, "callback")
        assert callable(cog.show_paste.callback)

    @pytest.mark.asyncio
    async def test_show_paste_embed_structure_complete(self, cog: GeneralCommands) -> None:
        """Test show_paste embed has all required components."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock()

        await cog.show_paste.callback(cog, mock_interaction)

        call_kwargs = mock_interaction.response.send_message.call_args[1]
        embed = call_kwargs["embed"]

        # Verify all components exist
        assert embed.title is not None
        assert embed.color is not None
        assert embed.thumbnail is not None
        assert len(embed.fields) == 2
        assert all(field.name for field in embed.fields)
        assert all(field.value for field in embed.fields)
