"""Tests for GitHub plugin commands and modals."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest
from discord import Interaction, Message, TextStyle
from discord.ext.commands import Bot

from byte_bot.plugins.github import GitHubCommands, GitHubIssue

if TYPE_CHECKING:
    pass


class TestGitHubIssue:
    """Tests for GitHubIssue modal."""

    @pytest.mark.asyncio
    async def test_modal_initialization_without_message(self) -> None:
        """Test modal initializes without message."""
        modal = GitHubIssue(title="Create GitHub Issue")

        assert modal.title == "Create GitHub Issue"
        assert modal.title_.label == "title"
        assert modal.description.label == "Description"
        assert modal.description.style == TextStyle.paragraph
        assert modal.mcve.label == "MCVE"
        assert modal.mcve.style == TextStyle.paragraph
        assert modal.logs.label == "Logs"
        assert modal.logs.style == TextStyle.paragraph
        assert modal.version.label == "Project Version"

    @pytest.mark.asyncio
    async def test_modal_initialization_with_message(self) -> None:
        """Test modal initializes with message content pre-filled."""
        mock_message = MagicMock(spec=Message)
        mock_message.content = "Test bug report"

        modal = GitHubIssue(title="Create GitHub Issue", message=mock_message)

        assert modal.description.default == "Test bug report"

    @pytest.mark.asyncio
    async def test_on_submit_sends_disabled_message(self) -> None:
        """Test on_submit sends message about feature being disabled."""
        modal = GitHubIssue(title="Create GitHub Issue")
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock()

        await modal.on_submit(mock_interaction)

        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert "temporarily disabled" in call_args[0][0].lower()
        assert call_args[1]["ephemeral"] is True

    @pytest.mark.asyncio
    async def test_on_submit_handles_exception(self) -> None:
        """Test on_submit handles exceptions gracefully."""
        modal = GitHubIssue(title="Create GitHub Issue")
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock(side_effect=Exception("Test error"))

        # Should not raise exception
        with pytest.raises(Exception, match="Test error"):
            await modal.on_submit(mock_interaction)


class TestGitHubCommands:
    """Tests for GitHubCommands cog."""

    @pytest.fixture
    def bot(self, mock_bot: Bot) -> Bot:
        """Create mock bot with tree."""
        mock_bot.tree = MagicMock()
        mock_bot.tree.add_command = MagicMock()
        return mock_bot

    @pytest.fixture
    def cog(self, bot: Bot) -> GitHubCommands:
        """Create GitHubCommands cog."""
        return GitHubCommands(bot)

    def test_cog_initialization(self, cog: GitHubCommands, bot: Bot) -> None:
        """Test cog initializes correctly."""
        assert cog.bot == bot
        assert cog.__cog_name__ == "GitHub Commands"
        assert cog.context_menu is not None
        assert cog.context_menu.name == "Create GitHub Issue"

    def test_cog_adds_context_menu_to_tree(self, cog: GitHubCommands, bot: Bot) -> None:
        """Test cog adds context menu command to bot tree."""
        bot.tree.add_command.assert_called_once()
        call_args = bot.tree.add_command.call_args[0]
        assert call_args[0] == cog.context_menu

    @pytest.mark.asyncio
    async def test_create_github_issue_modal(self, cog: GitHubCommands) -> None:
        """Test create_github_issue_modal sends modal to user."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_modal = AsyncMock()
        mock_message = MagicMock(spec=Message)
        mock_message.content = "Test message"

        await cog.create_github_issue_modal(mock_interaction, mock_message)

        mock_interaction.response.send_modal.assert_called_once()
        modal = mock_interaction.response.send_modal.call_args[0][0]
        assert isinstance(modal, GitHubIssue)
        assert modal.description.default == "Test message"

    @pytest.mark.asyncio
    async def test_create_github_issue_modal_without_message_content(self, cog: GitHubCommands) -> None:
        """Test create_github_issue_modal with empty message."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_modal = AsyncMock()
        mock_message = MagicMock(spec=Message)
        mock_message.content = ""

        await cog.create_github_issue_modal(mock_interaction, mock_message)

        mock_interaction.response.send_modal.assert_called_once()
        modal = mock_interaction.response.send_modal.call_args[0][0]
        assert isinstance(modal, GitHubIssue)
        assert modal.description.default == ""


def test_setup() -> None:
    """Test setup function registers cog."""
    bot = MagicMock()
    bot.add_cog = AsyncMock()
    bot.tree = MagicMock()
    bot.tree.add_command = MagicMock()

    # Call setup synchronously (it's async but we'll patch it)
    import asyncio

    from byte_bot.plugins.github import setup

    loop = asyncio.new_event_loop()
    loop.run_until_complete(setup(bot))
    loop.close()

    bot.add_cog.assert_called_once()
    cog = bot.add_cog.call_args[0][0]
    assert isinstance(cog, GitHubCommands)


class TestGitHubIssueEdgeCases:
    """Edge case tests for GitHubIssue modal."""

    @pytest.mark.asyncio
    async def test_modal_with_none_message(self) -> None:
        """Test modal handles None message gracefully."""
        modal = GitHubIssue(title="Create GitHub Issue", message=None)

        assert modal.title == "Create GitHub Issue"
        # Description should not have a default when message is None
        assert modal.description.default is None

    @pytest.mark.asyncio
    async def test_modal_with_empty_message_content(self) -> None:
        """Test modal handles message with empty content."""
        mock_message = MagicMock(spec=Message)
        mock_message.content = ""

        modal = GitHubIssue(title="Create GitHub Issue", message=mock_message)

        assert modal.description.default == ""

    @pytest.mark.asyncio
    async def test_modal_with_very_long_message(self) -> None:
        """Test modal handles very long message content."""
        mock_message = MagicMock(spec=Message)
        mock_message.content = "x" * 5000  # Very long content

        modal = GitHubIssue(title="Create GitHub Issue", message=mock_message)

        assert modal.description.default == "x" * 5000

    @pytest.mark.asyncio
    async def test_on_submit_interaction_error(self) -> None:
        """Test on_submit handles interaction.response.send_message failure."""
        modal = GitHubIssue(title="Create GitHub Issue")
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock(side_effect=Exception("Network error"))

        with pytest.raises(Exception, match="Network error"):
            await modal.on_submit(mock_interaction)

    @pytest.mark.asyncio
    async def test_on_submit_with_disabled_feature(self) -> None:
        """Test on_submit returns disabled message."""
        modal = GitHubIssue(title="Create GitHub Issue")

        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_message = AsyncMock()

        await modal.on_submit(mock_interaction)

        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert "temporarily disabled" in call_args[0][0].lower()


class TestGitHubCommandsEdgeCases:
    """Edge case tests for GitHubCommands cog."""

    @pytest.fixture
    def bot(self, mock_bot: Bot) -> Bot:
        """Create mock bot with tree."""
        mock_bot.tree = MagicMock()
        mock_bot.tree.add_command = MagicMock()
        return mock_bot

    @pytest.fixture
    def cog(self, bot: Bot) -> GitHubCommands:
        """Create GitHubCommands cog."""
        return GitHubCommands(bot)

    @pytest.mark.asyncio
    async def test_create_github_issue_modal_with_very_long_content(self, cog: GitHubCommands) -> None:
        """Test modal with extremely long message content."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_modal = AsyncMock()
        mock_message = MagicMock(spec=Message)
        mock_message.content = "A" * 10000  # Very long content

        await cog.create_github_issue_modal(mock_interaction, mock_message)

        mock_interaction.response.send_modal.assert_called_once()
        modal = mock_interaction.response.send_modal.call_args[0][0]
        assert isinstance(modal, GitHubIssue)
        assert modal.description.default == "A" * 10000

    @pytest.mark.asyncio
    async def test_create_github_issue_modal_with_special_characters(self, cog: GitHubCommands) -> None:
        """Test modal with special characters in message."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_modal = AsyncMock()
        mock_message = MagicMock(spec=Message)
        mock_message.content = "Test with special chars: @#$%^&*()[]{}|\\:;\"'<>,.?/~`"

        await cog.create_github_issue_modal(mock_interaction, mock_message)

        mock_interaction.response.send_modal.assert_called_once()
        modal = mock_interaction.response.send_modal.call_args[0][0]
        assert modal.description.default == "Test with special chars: @#$%^&*()[]{}|\\:;\"'<>,.?/~`"

    @pytest.mark.asyncio
    async def test_create_github_issue_modal_with_unicode(self, cog: GitHubCommands) -> None:
        """Test modal with unicode characters in message."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_modal = AsyncMock()
        mock_message = MagicMock(spec=Message)
        mock_message.content = "Unicode test: 你好世界 🌍 مرحبا"

        await cog.create_github_issue_modal(mock_interaction, mock_message)

        mock_interaction.response.send_modal.assert_called_once()
        modal = mock_interaction.response.send_modal.call_args[0][0]
        assert modal.description.default == "Unicode test: 你好世界 🌍 مرحبا"

    @pytest.mark.asyncio
    async def test_create_github_issue_modal_send_failure(self, cog: GitHubCommands) -> None:
        """Test create_github_issue_modal when sending modal fails."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_modal = AsyncMock(side_effect=Exception("Send failed"))
        mock_message = MagicMock(spec=Message)
        mock_message.content = "Test"

        with pytest.raises(Exception, match="Send failed"):
            await cog.create_github_issue_modal(mock_interaction, mock_message)

    def test_cog_context_menu_properties(self, cog: GitHubCommands) -> None:
        """Test context menu has correct properties."""
        assert cog.context_menu.name == "Create GitHub Issue"
        assert cog.context_menu.callback is not None
        assert callable(cog.context_menu.callback)

    @pytest.mark.asyncio
    async def test_create_github_issue_modal_with_whitespace_only(self, cog: GitHubCommands) -> None:
        """Test modal with whitespace-only message."""
        mock_interaction = MagicMock(spec=Interaction)
        mock_interaction.response.send_modal = AsyncMock()
        mock_message = MagicMock(spec=Message)
        mock_message.content = "   \n\t\r   "

        await cog.create_github_issue_modal(mock_interaction, mock_message)

        mock_interaction.response.send_modal.assert_called_once()
        modal = mock_interaction.response.send_modal.call_args[0][0]
        assert modal.description.default == "   \n\t\r   "
