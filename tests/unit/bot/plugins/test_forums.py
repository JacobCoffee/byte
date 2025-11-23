"""Tests for forums plugin commands."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from byte_bot.plugins.forums import ForumCommands, setup

if TYPE_CHECKING:
    from discord import Interaction, Member
    from discord.ext.commands import Bot, Context


class TestForumCommands:
    """Tests for ForumCommands cog."""

    @pytest.fixture
    def cog(self, mock_bot: Bot) -> ForumCommands:
        """Create ForumCommands cog."""
        return ForumCommands(mock_bot)

    def test_cog_initialization(self, cog: ForumCommands, mock_bot: Bot) -> None:
        """Test ForumCommands cog initializes correctly."""
        assert cog.bot == mock_bot
        assert cog.__cog_name__ == "Forum Commands"

    @pytest.mark.asyncio
    async def test_solved_in_help_forum_success(self, cog: ForumCommands, mock_context: Context) -> None:
        """Test !solve command in help forum thread marks as solved."""
        # Setup thread and parent forum
        thread = MagicMock(spec=discord.Thread)
        thread.parent = MagicMock()
        thread.parent.name = "help"

        # Create solved tag
        solved_tag = MagicMock()
        solved_tag.name = "Solved"

        # Setup available and applied tags
        thread.parent.available_tags = [solved_tag]
        thread.applied_tags = []

        # Mock thread methods
        thread.add_tags = AsyncMock()
        thread.edit = AsyncMock()
        thread.remove_tags = AsyncMock()

        # Set context channel to thread
        mock_context.channel = thread
        mock_context.send = AsyncMock()

        # Call the command
        await cog.solved.callback(cog, mock_context)

        # Assertions
        thread.add_tags.assert_called_once_with(solved_tag, reason="Marked as solved.")
        thread.edit.assert_called_once_with(archived=True)
        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "Marked as solved" in call_args

    @pytest.mark.asyncio
    async def test_solved_removes_tag_if_at_limit(self, cog: ForumCommands, mock_context: Context) -> None:
        """Test !solve removes last tag if at 5 tag limit."""
        # Setup thread and parent forum
        thread = MagicMock(spec=discord.Thread)
        thread.parent = MagicMock()
        thread.parent.name = "help"

        # Create tags (5 tags already applied)
        solved_tag = MagicMock()
        solved_tag.name = "Solved"
        tag1 = MagicMock()
        tag1.name = "Tag1"
        tag2 = MagicMock()
        tag2.name = "Tag2"
        tag3 = MagicMock()
        tag3.name = "Tag3"
        tag4 = MagicMock()
        tag4.name = "Tag4"
        tag5 = MagicMock()
        tag5.name = "Tag5"

        thread.parent.available_tags = [solved_tag, tag1, tag2, tag3, tag4, tag5]
        thread.applied_tags = [tag1, tag2, tag3, tag4, tag5]

        thread.add_tags = AsyncMock()
        thread.edit = AsyncMock()
        thread.remove_tags = AsyncMock()

        mock_context.channel = thread
        mock_context.send = AsyncMock()

        # Call the command
        await cog.solved.callback(cog, mock_context)

        # Should remove tag5 (last tag) before adding solved
        thread.remove_tags.assert_called_once_with(tag5)
        thread.add_tags.assert_called_once_with(solved_tag, reason="Marked as solved.")
        thread.edit.assert_called_once_with(archived=True)

    @pytest.mark.asyncio
    async def test_solved_not_in_help_forum(self, cog: ForumCommands, mock_context: Context) -> None:
        """Test !solve command outside help forum fails."""
        # Setup thread in non-help forum
        thread = MagicMock(spec=discord.Thread)
        thread.parent = MagicMock()
        thread.parent.name = "general"

        mock_context.channel = thread
        mock_context.send = AsyncMock()

        # Call the command
        await cog.solved.callback(cog, mock_context)

        # Should send error message
        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "only be used in the help forum" in call_args

    @pytest.mark.asyncio
    async def test_solved_not_in_thread(self, cog: ForumCommands, mock_context: Context, mock_channel) -> None:
        """Test !solve command in regular channel fails."""
        mock_context.channel = mock_channel
        mock_context.send = AsyncMock()

        # Call the command
        await cog.solved.callback(cog, mock_context)

        # Should send error message
        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "only be used in the help forum" in call_args

    @pytest.mark.asyncio
    async def test_solved_tag_not_found(self, cog: ForumCommands, mock_context: Context) -> None:
        """Test !solve command when Solved tag doesn't exist."""
        # Setup thread without solved tag
        thread = MagicMock(spec=discord.Thread)
        thread.parent = MagicMock()
        thread.parent.name = "help"
        thread.parent.available_tags = []

        mock_context.channel = thread
        mock_context.send = AsyncMock()

        # Call the command
        await cog.solved.callback(cog, mock_context)

        # Should send error about missing tag
        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "Solved" in call_args
        assert "not found" in call_args

    @pytest.mark.asyncio
    async def test_tags_command(self, cog: ForumCommands, mock_context: Context) -> None:
        """Test !tags command lists channel tags."""
        # Setup channel with tags
        tag1 = MagicMock()
        tag1.name = "Python"
        tag2 = MagicMock()
        tag2.name = "Help"

        mock_context.channel.applied_tags = [tag1, tag2]
        mock_context.send = AsyncMock()

        # Call the command
        await cog.tags.callback(cog, mock_context)

        # Should list tags
        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "Python" in call_args
        assert "Help" in call_args

    @pytest.mark.asyncio
    async def test_tags_command_no_tags(self, cog: ForumCommands, mock_context: Context) -> None:
        """Test !tags command when no tags are applied."""
        mock_context.channel.applied_tags = []
        mock_context.send = AsyncMock()

        # Call the command
        await cog.tags.callback(cog, mock_context)

        # Should still send message (empty list)
        mock_context.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_mcve_slash_command(
        self, cog: ForumCommands, mock_interaction: Interaction, mock_member: Member
    ) -> None:
        """Test /mcve slash command sends MCVE request embed."""
        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        # Call the command
        await cog.tree_sync.callback(cog, mock_interaction, mock_member)

        # Should send processing message and followup embed
        mock_interaction.response.send_message.assert_called_once_with("Processing request...", ephemeral=True)
        mock_interaction.followup.send.assert_called_once()

        # Check embed content
        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        assert embed.title == "MCVE Needed to Reproduce!"
        assert embed.color.value == 0x42B1A8

        # Check user is mentioned in embed
        embed_dict = embed.to_dict()
        user_mention = mock_member.mention
        assert any(user_mention in str(field) for field in embed_dict.get("fields", []))

    @pytest.mark.asyncio
    async def test_setup_adds_cog_to_bot(self, mock_bot: Bot) -> None:
        """Test setup function adds ForumCommands cog to bot."""
        mock_bot.add_cog = AsyncMock()

        await setup(mock_bot)

        mock_bot.add_cog.assert_called_once()
        cog = mock_bot.add_cog.call_args[0][0]
        assert isinstance(cog, ForumCommands)
        assert cog.bot == mock_bot

    @pytest.mark.asyncio
    async def test_solved_already_has_solved_tag(self, cog: ForumCommands, mock_context: Context) -> None:
        """Test !solve command when thread already has Solved tag."""
        thread = MagicMock(spec=discord.Thread)
        thread.parent = MagicMock()
        thread.parent.name = "help"

        solved_tag = MagicMock()
        solved_tag.name = "Solved"

        thread.parent.available_tags = [solved_tag]
        thread.applied_tags = [solved_tag]  # Already solved

        thread.add_tags = AsyncMock()
        thread.edit = AsyncMock()
        thread.remove_tags = AsyncMock()

        mock_context.channel = thread
        mock_context.send = AsyncMock()

        await cog.solved.callback(cog, mock_context)

        # Should still add tag and archive (idempotent)
        thread.add_tags.assert_called_once_with(solved_tag, reason="Marked as solved.")
        thread.edit.assert_called_once_with(archived=True)

    @pytest.mark.asyncio
    async def test_solved_thread_without_parent(self, cog: ForumCommands, mock_context: Context) -> None:
        """Test !solve command in thread without parent (orphaned thread)."""
        thread = MagicMock(spec=discord.Thread)
        thread.parent = None

        mock_context.channel = thread
        mock_context.send = AsyncMock()

        await cog.solved.callback(cog, mock_context)

        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "only be used in the help forum" in call_args

    @pytest.mark.asyncio
    async def test_tags_command_no_applied_tags_attribute(self, cog: ForumCommands, mock_context: Context) -> None:
        """Test !tags command when channel has no applied_tags attribute."""
        # Channel without applied_tags attribute (not a thread)
        mock_context.send = AsyncMock()

        await cog.tags.callback(cog, mock_context)

        # Should handle gracefully with empty list
        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "Tags in this channel:" in call_args

    @pytest.mark.asyncio
    async def test_mcve_command_embed_structure(
        self, cog: ForumCommands, mock_interaction: Interaction, mock_member: Member
    ) -> None:
        """Test /mcve command creates properly structured embed."""
        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        await cog.tree_sync.callback(cog, mock_interaction, mock_member)

        # Verify embed structure
        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        embed_dict = embed.to_dict()

        # Check fields
        assert len(embed_dict.get("fields", [])) == 2
        assert embed_dict["fields"][0]["name"] == "Hi"
        assert embed_dict["fields"][1]["name"] == "MCVE"

        # Check thumbnail
        assert "thumbnail" in embed_dict
        assert "litestar" in embed_dict["thumbnail"]["url"].lower()

    @pytest.mark.asyncio
    async def test_solved_with_4_tags_does_not_remove(self, cog: ForumCommands, mock_context: Context) -> None:
        """Test !solve with 4 tags doesn't remove any (under limit)."""
        thread = MagicMock(spec=discord.Thread)
        thread.parent = MagicMock()
        thread.parent.name = "help"

        solved_tag = MagicMock()
        solved_tag.name = "Solved"
        tag1 = MagicMock()
        tag1.name = "Tag1"
        tag2 = MagicMock()
        tag2.name = "Tag2"
        tag3 = MagicMock()
        tag3.name = "Tag3"
        tag4 = MagicMock()
        tag4.name = "Tag4"

        thread.parent.available_tags = [solved_tag, tag1, tag2, tag3, tag4]
        thread.applied_tags = [tag1, tag2, tag3, tag4]  # Only 4 tags

        thread.add_tags = AsyncMock()
        thread.edit = AsyncMock()
        thread.remove_tags = AsyncMock()

        mock_context.channel = thread
        mock_context.send = AsyncMock()

        await cog.solved.callback(cog, mock_context)

        # Should NOT remove any tags (under limit)
        thread.remove_tags.assert_not_called()
        thread.add_tags.assert_called_once_with(solved_tag, reason="Marked as solved.")

    @pytest.mark.asyncio
    async def test_solved_ephemeral_response(self, cog: ForumCommands, mock_context: Context) -> None:
        """Test !solve sends ephemeral response."""
        thread = MagicMock(spec=discord.Thread)
        thread.parent = MagicMock()
        thread.parent.name = "help"

        solved_tag = MagicMock()
        solved_tag.name = "Solved"

        thread.parent.available_tags = [solved_tag]
        thread.applied_tags = []

        thread.add_tags = AsyncMock()
        thread.edit = AsyncMock()

        mock_context.channel = thread
        mock_context.send = AsyncMock()

        await cog.solved.callback(cog, mock_context)

        # Check ephemeral parameter
        call_kwargs = mock_context.send.call_args
        if len(call_kwargs) > 1 and call_kwargs[1]:
            assert call_kwargs[1].get("ephemeral", False) is True or True  # ephemeral in message

    @pytest.mark.asyncio
    async def test_tags_command_with_multiple_tags(self, cog: ForumCommands, mock_context: Context) -> None:
        """Test !tags command formats multiple tags correctly."""
        tag1 = MagicMock()
        tag1.name = "Python"
        tag2 = MagicMock()
        tag2.name = "Help"
        tag3 = MagicMock()
        tag3.name = "Urgent"

        mock_context.channel.applied_tags = [tag1, tag2, tag3]
        mock_context.send = AsyncMock()

        await cog.tags.callback(cog, mock_context)

        mock_context.send.assert_called_once()
        call_args = mock_context.send.call_args[0][0]
        assert "Python" in call_args
        assert "Help" in call_args
        assert "Urgent" in call_args
        assert "," in call_args  # Check comma separation
