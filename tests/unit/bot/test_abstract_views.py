"""Tests for Discord UI abstract views and embeds."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest
from discord import ButtonStyle, Colour, Embed

from byte_bot.views.abstract_views import ButtonEmbedView, ExtendedEmbed, Field

if TYPE_CHECKING:
    from discord.ext.commands import Bot


class TestButtonEmbedView:
    """Tests for ButtonEmbedView class."""

    @pytest.fixture
    def original_embed(self) -> Embed:
        """Create original embed fixture."""
        embed = Embed(title="Original Title", description="Full description with lots of details", colour=Colour.blue())
        embed.add_field(name="Field 1", value="Value 1")
        embed.add_field(name="Field 2", value="Value 2")
        return embed

    @pytest.fixture
    def minified_embed(self) -> Embed:
        """Create minified embed fixture."""
        return Embed(title="Short Title", description="Brief description", colour=Colour.green())

    @pytest.fixture
    def view(self, mock_bot: Bot, original_embed: Embed, minified_embed: Embed) -> ButtonEmbedView:
        """Create ButtonEmbedView instance."""
        return ButtonEmbedView(
            author=987654321,
            bot=mock_bot,
            original_embed=original_embed,
            minified_embed=minified_embed,
        )

    def test_initialization(
        self, view: ButtonEmbedView, mock_bot: Bot, original_embed: Embed, minified_embed: Embed
    ) -> None:
        """Test view initialization with all parameters."""
        assert view.author_id == 987654321
        assert view.bot == mock_bot
        assert view.original_embed == original_embed
        assert view.minified_embed == minified_embed

    async def test_delete_interaction_check_author_allowed(self, view: ButtonEmbedView) -> None:
        """Test delete check allows author."""
        interaction = MagicMock()
        interaction.user.id = 987654321  # Same as author_id

        result = await view.delete_interaction_check(interaction)

        assert result is True
        interaction.response.send_message.assert_not_called()

    async def test_delete_interaction_check_admin_allowed(self, view: ButtonEmbedView) -> None:
        """Test delete check allows guild admin."""
        interaction = MagicMock()
        interaction.user.id = 111111111  # Different from author
        interaction.user.guild_permissions = MagicMock()
        interaction.user.guild_permissions.administrator = True

        result = await view.delete_interaction_check(interaction)

        assert result is True
        interaction.response.send_message.assert_not_called()

    async def test_delete_interaction_check_other_user_denied(self, view: ButtonEmbedView) -> None:
        """Test delete check denies non-admin, non-author user."""
        interaction = MagicMock()
        interaction.user.id = 111111111  # Different from author
        interaction.user.guild_permissions = MagicMock()
        interaction.user.guild_permissions.administrator = False
        interaction.response.send_message = AsyncMock()

        result = await view.delete_interaction_check(interaction)

        assert result is False
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        assert "permission" in call_args[1]["ephemeral"] or call_args[0][0]
        assert call_args[1]["ephemeral"] is True

    async def test_delete_interaction_check_no_guild_permissions(self, view: ButtonEmbedView) -> None:
        """Test delete check handles user without guild_permissions attribute."""
        interaction = MagicMock()
        interaction.user.id = 111111111  # Different from author
        # No guild_permissions attribute (like in DMs)
        del interaction.user.guild_permissions
        interaction.response.send_message = AsyncMock()

        result = await view.delete_interaction_check(interaction)

        assert result is False

    async def test_delete_button_callback_success(self, view: ButtonEmbedView) -> None:
        """Test delete button callback deletes message."""
        interaction = MagicMock()
        interaction.user.id = 987654321  # Author
        interaction.message = MagicMock()
        interaction.message.delete = AsyncMock()

        await view.delete_button_callback(interaction)

        interaction.message.delete.assert_called_once()

    async def test_delete_button_callback_no_message(self, view: ButtonEmbedView) -> None:
        """Test delete button callback handles missing message."""
        interaction = MagicMock()
        interaction.user.id = 987654321  # Author
        interaction.message = None

        # Should not raise exception
        await view.delete_button_callback(interaction)

    async def test_delete_button_callback_unauthorized(self, view: ButtonEmbedView) -> None:
        """Test delete button callback respects permissions."""
        interaction = MagicMock()
        interaction.user.id = 111111111  # Not author
        interaction.user.guild_permissions = MagicMock()
        interaction.user.guild_permissions.administrator = False
        interaction.response.send_message = AsyncMock()
        interaction.message = MagicMock()
        interaction.message.delete = AsyncMock()

        await view.delete_button_callback(interaction)

        # Message should not be deleted
        interaction.message.delete.assert_not_called()

    async def test_learn_more_button_callback(self, view: ButtonEmbedView, original_embed: Embed) -> None:
        """Test learn more button sends original embed ephemerally."""
        interaction = MagicMock()
        interaction.response.send_message = AsyncMock()

        await view.learn_more_button_callback(interaction)

        interaction.response.send_message.assert_called_once_with(embed=original_embed, ephemeral=True)

    async def test_delete_button_decorator(self, view: ButtonEmbedView) -> None:
        """Test delete button is properly configured."""
        # Find the delete button
        delete_button = None
        for item in view.children:
            if hasattr(item, "custom_id") and item.custom_id == "delete_button":
                delete_button = item
                break

        assert delete_button is not None
        assert delete_button.label == "Delete"
        assert delete_button.style == ButtonStyle.red

    async def test_learn_more_button_decorator(self, view: ButtonEmbedView) -> None:
        """Test learn more button is properly configured."""
        # Find the learn more button
        learn_more_button = None
        for item in view.children:
            if hasattr(item, "custom_id") and item.custom_id == "learn_more_button":
                learn_more_button = item
                break

        assert learn_more_button is not None
        assert learn_more_button.label == "Learn More"
        assert learn_more_button.style == ButtonStyle.green


class TestField:
    """Tests for Field TypedDict."""

    def test_field_structure(self) -> None:
        """Test Field has correct structure."""
        field: Field = {
            "name": "Test Field",
            "value": "Test Value",
            "inline": True,
        }

        assert field["name"] == "Test Field"
        assert field["value"] == "Test Value"
        assert field["inline"] is True

    def test_field_without_inline(self) -> None:
        """Test Field works without inline (NotRequired)."""
        field: Field = {
            "name": "Test Field",
            "value": "Test Value",
        }

        assert field["name"] == "Test Field"
        assert field["value"] == "Test Value"
        assert "inline" not in field


class TestExtendedEmbed:
    """Tests for ExtendedEmbed class."""

    def test_add_field_dict_single(self) -> None:
        """Test adding single field via dictionary."""
        embed = ExtendedEmbed(title="Test")
        field: Field = {"name": "Field 1", "value": "Value 1", "inline": False}

        result = embed.add_field_dict(field)

        assert result is embed  # Returns self
        assert len(embed.fields) == 1
        assert embed.fields[0].name == "Field 1"
        assert embed.fields[0].value == "Value 1"
        assert embed.fields[0].inline is False

    def test_add_field_dict_without_inline(self) -> None:
        """Test adding field without inline parameter."""
        embed = ExtendedEmbed(title="Test")
        field: Field = {"name": "Field 1", "value": "Value 1"}

        embed.add_field_dict(field)

        assert len(embed.fields) == 1
        # Discord defaults inline to True
        assert embed.fields[0].inline is True

    def test_add_field_dicts_multiple(self) -> None:
        """Test adding multiple fields via list of dictionaries."""
        embed = ExtendedEmbed(title="Test")
        fields: list[Field] = [
            {"name": "Field 1", "value": "Value 1", "inline": True},
            {"name": "Field 2", "value": "Value 2", "inline": False},
            {"name": "Field 3", "value": "Value 3"},
        ]

        result = embed.add_field_dicts(fields)

        assert result is embed  # Returns self
        assert len(embed.fields) == 3
        assert embed.fields[0].name == "Field 1"
        assert embed.fields[1].name == "Field 2"
        assert embed.fields[2].name == "Field 3"

    def test_add_field_dicts_empty_list(self) -> None:
        """Test adding empty list of fields."""
        embed = ExtendedEmbed(title="Test")

        result = embed.add_field_dicts([])

        assert result is embed
        assert len(embed.fields) == 0

    def test_from_field_dicts_with_fields(self) -> None:
        """Test creating embed from field dictionaries."""
        fields: list[Field] = [
            {"name": "Field 1", "value": "Value 1", "inline": True},
            {"name": "Field 2", "value": "Value 2", "inline": False},
        ]

        embed = ExtendedEmbed.from_field_dicts(
            title="Test Title",
            description="Test Description",
            colour=Colour.blue(),
            fields=fields,
        )

        assert embed.title == "Test Title"
        assert embed.description == "Test Description"
        assert embed.colour == Colour.blue()
        assert len(embed.fields) == 2
        assert embed.fields[0].name == "Field 1"
        assert embed.fields[1].name == "Field 2"

    def test_from_field_dicts_without_fields(self) -> None:
        """Test creating embed without fields parameter."""
        embed = ExtendedEmbed.from_field_dicts(
            title="Test Title",
            description="Test Description",
        )

        assert embed.title == "Test Title"
        assert embed.description == "Test Description"
        assert len(embed.fields) == 0

    def test_from_field_dicts_with_color_alias(self) -> None:
        """Test creating embed with 'color' parameter (American spelling)."""
        embed = ExtendedEmbed.from_field_dicts(
            title="Test",
            color=Colour.red(),
        )

        assert embed.colour == Colour.red()

    def test_from_field_dicts_with_url(self) -> None:
        """Test creating embed with URL."""
        embed = ExtendedEmbed.from_field_dicts(
            title="Test",
            url="https://example.com",
        )

        assert embed.url == "https://example.com"

    def test_from_field_dicts_with_timestamp(self) -> None:
        """Test creating embed with timestamp."""
        from datetime import datetime

        timestamp = datetime.now(UTC)
        embed = ExtendedEmbed.from_field_dicts(
            title="Test",
            timestamp=timestamp,
        )

        assert embed.timestamp == timestamp

    def test_deepcopy_basic(self) -> None:
        """Test deep copying embed."""
        original = ExtendedEmbed(
            title="Original",
            description="Original Description",
            colour=Colour.blue(),
        )
        original.add_field(name="Field 1", value="Value 1")

        copied = original.deepcopy()

        assert copied.title == original.title
        assert copied.description == original.description
        assert copied.colour == original.colour
        assert len(copied.fields) == len(original.fields)
        assert copied is not original  # Different objects

    def test_deepcopy_modifications_independent(self) -> None:
        """Test modifications to copied embed don't affect original."""
        original = ExtendedEmbed(title="Original")
        original.add_field(name="Original Field", value="Original Value")

        copied = original.deepcopy()
        copied.title = "Modified"
        copied.add_field(name="New Field", value="New Value")

        assert original.title == "Original"
        assert len(original.fields) == 1
        assert len(copied.fields) == 2

    def test_deepcopy_uses_standard_deepcopy(self) -> None:
        """Test deepcopy method uses copy.deepcopy."""
        embed = ExtendedEmbed(title="Test")
        copied = embed.deepcopy()

        # Verify it's a deep copy
        assert copied == deepcopy(embed)

    def test_chaining_methods(self) -> None:
        """Test method chaining works correctly."""
        field1: Field = {"name": "Field 1", "value": "Value 1"}
        field2: Field = {"name": "Field 2", "value": "Value 2"}

        embed = ExtendedEmbed(title="Test").add_field_dict(field1).add_field_dict(field2)

        assert len(embed.fields) == 2

    def test_extends_discord_embed(self) -> None:
        """Test ExtendedEmbed is a subclass of discord.Embed."""
        embed = ExtendedEmbed(title="Test")

        assert isinstance(embed, Embed)

    def test_all_embed_types(self) -> None:
        """Test creation with all embed types."""
        types = ["rich", "image", "video", "gifv", "article", "link"]

        for embed_type in types:
            embed = ExtendedEmbed.from_field_dicts(
                title="Test",
                type=embed_type,  # type: ignore[arg-type]
            )
            assert embed.type == embed_type
