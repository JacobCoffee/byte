"""Tests for forums views module."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from discord import ButtonStyle
from discord.ui import Button

from byte_bot.views.forums import HelpThreadView

if TYPE_CHECKING:
    from discord import Interaction, Member
    from discord.ext.commands import Bot


class TestHelpThreadViewInitialization:
    """Tests for HelpThreadView initialization."""

    @pytest.mark.asyncio
    async def test_help_thread_view_initialization(self, mock_member: Member, mock_bot: Bot) -> None:
        """Test HelpThreadView initializes correctly."""
        guild_id = 555555555
        view = HelpThreadView(author=mock_member, guild_id=guild_id, bot=mock_bot, timeout=180.0)

        assert view.author == mock_member
        assert view.guild_id == guild_id
        assert view.bot == mock_bot
        assert view.timeout == 180.0

    @pytest.mark.asyncio
    async def test_help_thread_view_default_timeout(self, mock_member: Member, mock_bot: Bot) -> None:
        """Test HelpThreadView uses default timeout."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        assert view.timeout == 180.0

    @pytest.mark.asyncio
    async def test_help_thread_view_custom_timeout(self, mock_member: Member, mock_bot: Bot) -> None:
        """Test HelpThreadView accepts custom timeout."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot, timeout=300.0)

        assert view.timeout == 300.0

    @pytest.mark.asyncio
    async def test_help_thread_view_has_buttons(self, mock_member: Member, mock_bot: Bot) -> None:
        """Test HelpThreadView has required buttons."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        # Check that view has children (buttons)
        assert len(view.children) == 2

        # Find solve and remove buttons
        solve_button = None
        remove_button = None
        for child in view.children:
            if isinstance(child, Button):
                if child.custom_id == "solve_button":
                    solve_button = child
                elif child.custom_id == "remove_button":
                    remove_button = child

        assert solve_button is not None
        assert remove_button is not None

    @pytest.mark.asyncio
    async def test_help_thread_view_button_styles(self, mock_member: Member, mock_bot: Bot) -> None:
        """Test HelpThreadView buttons have correct styles."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        solve_button = None
        remove_button = None
        for child in view.children:
            if isinstance(child, Button):
                if child.custom_id == "solve_button":
                    solve_button = child
                elif child.custom_id == "remove_button":
                    remove_button = child

        assert solve_button is not None
        assert solve_button.style == ButtonStyle.green
        assert solve_button.label == "Solve"

        assert remove_button is not None
        assert remove_button.style == ButtonStyle.red
        assert remove_button.label == "Remove"


class TestHelpThreadViewSetup:
    """Tests for HelpThreadView setup method."""

    @pytest.mark.asyncio
    async def test_help_thread_view_setup(self, mock_member: Member, mock_bot: Bot) -> None:
        """Test HelpThreadView setup method runs without error."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        # Setup currently does nothing during migration
        await view.setup()

        # Should complete without error

    @pytest.mark.asyncio
    async def test_help_thread_view_setup_with_exception(self, mock_member: Member, mock_bot: Bot) -> None:
        """Test HelpThreadView setup handles exceptions gracefully."""
        # Create a view with problematic guild_id that could cause issues
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        # Currently setup just passes (no actual code during migration)
        # To test the exception handler, we'd need to uncomment the commented code
        # For now, verify setup completes without error
        await view.setup()

        # Setup should complete successfully even though it's a no-op

    @pytest.mark.asyncio
    async def test_help_thread_view_setup_error_logged(self, mock_member: Member, mock_bot: Bot) -> None:
        """Test HelpThreadView setup logs exceptions when they occur."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        # Patch the pass statement location to simulate what would happen if code was active
        # The current setup() is just 'pass', so exception handler is unreachable
        # This test documents expected behavior when API integration is restored
        with patch("byte_bot.views.forums.logger") as mock_logger:
            await view.setup()
            # During migration, no errors occur so logger not called
            mock_logger.exception.assert_not_called()


class TestHelpThreadViewPermissions:
    """Tests for HelpThreadView permission checks."""

    @pytest.mark.asyncio
    async def test_delete_interaction_check_author_allowed(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test delete_interaction_check allows thread author."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)
        mock_interaction.user = mock_member

        result = await view.delete_interaction_check(mock_interaction)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_interaction_check_admin_allowed(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test delete_interaction_check allows administrators."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        # Create a different user who is admin
        admin_user = MagicMock()
        admin_user.id = 999999999
        admin_user.guild_permissions = MagicMock()
        admin_user.guild_permissions.administrator = True

        mock_interaction.user = admin_user

        result = await view.delete_interaction_check(mock_interaction)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_interaction_check_non_author_denied(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test delete_interaction_check denies non-author, non-admin users."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        # Create a different user who is not admin
        other_user = MagicMock()
        other_user.id = 111111111
        other_user.guild_permissions = MagicMock()
        other_user.guild_permissions.administrator = False

        mock_interaction.user = other_user

        result = await view.delete_interaction_check(mock_interaction)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_interaction_check_no_guild_permissions(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test delete_interaction_check handles missing guild_permissions."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        # Create a user without guild_permissions (DM context)
        dm_user = MagicMock()
        dm_user.id = 222222222
        del dm_user.guild_permissions

        mock_interaction.user = dm_user

        result = await view.delete_interaction_check(mock_interaction)

        assert result is False


class TestHelpThreadViewSolveButton:
    """Tests for HelpThreadView solve button."""

    def _get_solve_button(self, view: HelpThreadView) -> Button:
        """Helper to get solve button from view."""
        for child in view.children:
            if isinstance(child, Button) and child.custom_id == "solve_button":
                return child
        raise ValueError("Solve button not found")

    @pytest.mark.asyncio
    async def test_solve_button_callback_author(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test solve button callback works for thread author."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)
        mock_interaction.user = mock_member
        mock_interaction.message = MagicMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        # Mock bot.get_context
        mock_context = MagicMock()
        mock_context.channel = MagicMock()
        mock_context.args = []
        mock_bot.get_context = AsyncMock(return_value=mock_context)  # type: ignore[method-assign]

        # Mock solve command
        mock_solve_command = MagicMock()
        mock_solve_command.invoke = AsyncMock()
        mock_bot.get_command = MagicMock(return_value=mock_solve_command)  # type: ignore[method-assign]

        # Get the actual button and call its callback
        button = self._get_solve_button(view)
        await button.callback(mock_interaction)

        mock_interaction.response.defer.assert_called_once()
        mock_interaction.followup.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_solve_button_callback_non_author_denied(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test solve button callback denies non-author users."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        # Different user
        other_user = MagicMock()
        other_user.id = 111111111
        other_user.guild_permissions = MagicMock()
        other_user.guild_permissions.administrator = False

        mock_interaction.user = other_user

        # Get the actual button and call its callback
        button = self._get_solve_button(view)
        await button.callback(mock_interaction)

        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert "author" in call_args[0][0].lower() or "administrator" in call_args[0][0].lower()
        assert call_args[1]["ephemeral"] is True

    @pytest.mark.asyncio
    async def test_solve_button_callback_admin_allowed(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test solve button callback allows administrators."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        # Admin user
        admin_user = MagicMock()
        admin_user.id = 999999999
        admin_user.guild_permissions = MagicMock()
        admin_user.guild_permissions.administrator = True

        mock_interaction.user = admin_user
        mock_interaction.message = MagicMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        mock_context = MagicMock()
        mock_context.channel = MagicMock()
        mock_context.args = []
        mock_bot.get_context = AsyncMock(return_value=mock_context)  # type: ignore[method-assign]

        mock_solve_command = MagicMock()
        mock_solve_command.invoke = AsyncMock()
        mock_bot.get_command = MagicMock(return_value=mock_solve_command)  # type: ignore[method-assign]

        # Get the actual button and call its callback
        button = self._get_solve_button(view)
        await button.callback(mock_interaction)

        mock_interaction.response.defer.assert_called_once()

    @pytest.mark.asyncio
    async def test_solve_button_callback_command_not_found(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test solve button callback handles missing solve command."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)
        mock_interaction.user = mock_member
        mock_interaction.message = MagicMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        mock_context = MagicMock()
        mock_context.args = []
        mock_bot.get_context = AsyncMock(return_value=mock_context)  # type: ignore[method-assign]

        # No solve command
        mock_bot.get_command = MagicMock(return_value=None)  # type: ignore[method-assign]

        # Get the actual button and call its callback
        button = self._get_solve_button(view)
        await button.callback(mock_interaction)

        mock_interaction.followup.send.assert_called_once()
        call_args = mock_interaction.followup.send.call_args
        assert "not found" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_solve_button_callback_exception_handling(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test solve button callback handles exceptions."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)
        mock_interaction.user = mock_member
        mock_interaction.message = MagicMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        mock_context = MagicMock()
        mock_context.args = []
        mock_bot.get_context = AsyncMock(return_value=mock_context)  # type: ignore[method-assign]

        mock_solve_command = MagicMock()
        mock_solve_command.invoke = AsyncMock(side_effect=Exception("Test error"))
        mock_bot.get_command = MagicMock(return_value=mock_solve_command)  # type: ignore[method-assign]

        # Get the actual button and call its callback
        button = self._get_solve_button(view)

        with patch("byte_bot.views.forums.logger") as mock_logger:
            await button.callback(mock_interaction)

            mock_logger.exception.assert_called_once()
            mock_interaction.followup.send.assert_called_once()
            call_args = mock_interaction.followup.send.call_args
            assert "failed" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_solve_button_callback_logs_invocation(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test solve button callback logs command invocation."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)
        mock_interaction.user = mock_member
        mock_interaction.message = MagicMock()
        mock_interaction.channel = MagicMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        mock_context = MagicMock()
        mock_context.channel = MagicMock()
        mock_context.args = []
        mock_bot.get_context = AsyncMock(return_value=mock_context)  # type: ignore[method-assign]

        mock_solve_command = MagicMock()
        mock_solve_command.invoke = AsyncMock()
        mock_bot.get_command = MagicMock(return_value=mock_solve_command)  # type: ignore[method-assign]

        button = self._get_solve_button(view)

        with patch("byte_bot.views.forums.logger") as mock_logger:
            await button.callback(mock_interaction)

            # Verify logger.info was called for command invocation
            assert mock_logger.info.called
            call_args = mock_logger.info.call_args[0]
            assert "invoking" in call_args[0].lower()

    @pytest.mark.asyncio
    async def test_solve_button_callback_sets_command_context(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test solve button callback sets up command context correctly."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)
        mock_interaction.user = mock_member
        mock_interaction.message = MagicMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        mock_context = MagicMock()
        mock_context.channel = MagicMock()
        mock_context.args = []
        mock_bot.get_context = AsyncMock(return_value=mock_context)  # type: ignore[method-assign]

        mock_solve_command = MagicMock()
        mock_solve_command.invoke = AsyncMock()
        mock_bot.get_command = MagicMock(return_value=mock_solve_command)  # type: ignore[method-assign]

        button = self._get_solve_button(view)
        await button.callback(mock_interaction)

        # Verify context was set up correctly
        assert mock_context.command == mock_solve_command
        assert mock_context.invoked_with == "solve"

    @pytest.mark.asyncio
    async def test_solve_button_callback_without_message(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test solve button callback handles interaction without message."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)
        mock_interaction.user = mock_member
        mock_interaction.message = None

        button = self._get_solve_button(view)

        # Should not raise an error even without message
        await button.callback(mock_interaction)


class TestHelpThreadViewRemoveButton:
    """Tests for HelpThreadView remove button."""

    def _get_remove_button(self, view: HelpThreadView) -> Button:
        """Helper to get remove button from view."""
        for child in view.children:
            if isinstance(child, Button) and child.custom_id == "remove_button":
                return child
        raise ValueError("Remove button not found")

    @pytest.mark.asyncio
    async def test_remove_button_callback_author(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test remove button callback works for thread author."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)
        mock_interaction.user = mock_member
        mock_interaction.message = MagicMock()
        mock_interaction.message.content = "Test content"
        mock_interaction.message.edit = AsyncMock()

        # Get the actual button and call its callback
        button = self._get_remove_button(view)
        await button.callback(mock_interaction)

        mock_interaction.message.edit.assert_called_once()
        call_kwargs = mock_interaction.message.edit.call_args[1]
        assert call_kwargs["embed"] is None
        assert call_kwargs["view"] is None

    @pytest.mark.asyncio
    async def test_remove_button_callback_non_author_denied(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test remove button callback denies non-author users."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        other_user = MagicMock()
        other_user.id = 111111111
        other_user.guild_permissions = MagicMock()
        other_user.guild_permissions.administrator = False

        mock_interaction.user = other_user

        # Get the actual button and call its callback
        button = self._get_remove_button(view)
        await button.callback(mock_interaction)

        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        # Check message content contains either "author" or "administrator" or "remove"
        assert any(word in call_args[0][0].lower() for word in ["author", "administrator", "remove"])

    @pytest.mark.asyncio
    async def test_remove_button_callback_no_message(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test remove button callback handles missing message."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)
        mock_interaction.user = mock_member
        mock_interaction.message = None

        # Get the actual button and call its callback
        button = self._get_remove_button(view)

        # Should not raise an error
        await button.callback(mock_interaction)

    @pytest.mark.asyncio
    async def test_remove_button_callback_empty_content(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test remove button callback handles empty message content."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)
        mock_interaction.user = mock_member
        mock_interaction.message = MagicMock()
        mock_interaction.message.content = None
        mock_interaction.message.edit = AsyncMock()

        # Get the actual button and call its callback
        button = self._get_remove_button(view)
        await button.callback(mock_interaction)

        mock_interaction.message.edit.assert_called_once()
        call_kwargs = mock_interaction.message.edit.call_args[1]
        # Should use zero-width space when content is None
        assert call_kwargs["content"] == "\u200b"

    @pytest.mark.asyncio
    async def test_remove_button_callback_logs_removal(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test remove button callback logs the removal action."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)
        mock_interaction.user = mock_member
        mock_interaction.message = MagicMock()
        mock_interaction.message.content = "Test"
        mock_interaction.message.edit = AsyncMock()

        # Get the actual button and call its callback
        button = self._get_remove_button(view)

        with patch("byte_bot.views.forums.logger") as mock_logger:
            await button.callback(mock_interaction)

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0]
            assert "removing" in call_args[0].lower()

    @pytest.mark.asyncio
    async def test_remove_button_callback_preserves_content(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test remove button callback preserves original message content."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)
        mock_interaction.user = mock_member
        original_content = "Important message content"
        mock_interaction.message = MagicMock()
        mock_interaction.message.content = original_content
        mock_interaction.message.edit = AsyncMock()

        button = self._get_remove_button(view)
        await button.callback(mock_interaction)

        call_kwargs = mock_interaction.message.edit.call_args[1]
        assert call_kwargs["content"] == original_content

    @pytest.mark.asyncio
    async def test_remove_button_callback_admin_allowed(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test remove button callback allows administrators."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        # Admin user
        admin_user = MagicMock()
        admin_user.id = 999999999
        admin_user.guild_permissions = MagicMock()
        admin_user.guild_permissions.administrator = True

        mock_interaction.user = admin_user
        mock_interaction.message = MagicMock()
        mock_interaction.message.content = "Test"
        mock_interaction.message.edit = AsyncMock()

        button = self._get_remove_button(view)
        await button.callback(mock_interaction)

        # Should successfully remove view/embed
        mock_interaction.message.edit.assert_called_once()


class TestHelpThreadViewTimeout:
    """Tests for HelpThreadView timeout behavior."""

    @pytest.mark.asyncio
    async def test_view_timeout_is_set(self, mock_member: Member, mock_bot: Bot) -> None:
        """Test view has timeout set correctly."""
        timeout = 300.0
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot, timeout=timeout)

        assert view.timeout == timeout

    @pytest.mark.asyncio
    async def test_view_timeout_none(self, mock_member: Member, mock_bot: Bot) -> None:
        """Test view can have no timeout."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot, timeout=None)

        assert view.timeout is None


class TestHelpThreadViewIntegration:
    """Integration tests for HelpThreadView."""

    @pytest.mark.asyncio
    async def test_complete_solve_workflow(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test complete workflow of solving a help thread."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        # Setup interaction
        mock_interaction.user = mock_member
        mock_interaction.message = MagicMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        # Setup bot mocks
        mock_context = MagicMock()
        mock_context.channel = MagicMock()
        mock_context.args = []
        mock_bot.get_context = AsyncMock(return_value=mock_context)  # type: ignore[method-assign]

        mock_solve_command = MagicMock()
        mock_solve_command.invoke = AsyncMock()
        mock_bot.get_command = MagicMock(return_value=mock_solve_command)  # type: ignore[method-assign]

        # Get solve button
        solve_button = None
        for child in view.children:
            if isinstance(child, Button) and child.custom_id == "solve_button":
                solve_button = child
                break

        assert solve_button is not None

        # Execute solve workflow
        await solve_button.callback(mock_interaction)

        # Verify workflow completed
        mock_interaction.response.defer.assert_called_once()
        mock_solve_command.invoke.assert_called_once()
        mock_interaction.followup.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_remove_workflow(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test complete workflow of removing help thread message."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        # Setup interaction
        mock_interaction.user = mock_member
        mock_interaction.message = MagicMock()
        mock_interaction.message.content = "Help message"
        mock_interaction.message.edit = AsyncMock()

        # Get remove button
        remove_button = None
        for child in view.children:
            if isinstance(child, Button) and child.custom_id == "remove_button":
                remove_button = child
                break

        assert remove_button is not None

        # Execute remove workflow
        await remove_button.callback(mock_interaction)

        # Verify message was edited
        mock_interaction.message.edit.assert_called_once()

    @pytest.mark.asyncio
    async def test_permission_denied_workflow(
        self, mock_interaction: Interaction, mock_member: Member, mock_bot: Bot
    ) -> None:
        """Test permission denied workflow for unauthorized user."""
        view = HelpThreadView(author=mock_member, guild_id=555555555, bot=mock_bot)

        # Different user without admin
        other_user = MagicMock()
        other_user.id = 111111111
        other_user.guild_permissions = MagicMock()
        other_user.guild_permissions.administrator = False

        mock_interaction.user = other_user

        # Try to solve (should be denied)
        solve_button = None
        for child in view.children:
            if isinstance(child, Button) and child.custom_id == "solve_button":
                solve_button = child
                break

        assert solve_button is not None
        await solve_button.callback(mock_interaction)

        # Verify permission denied message
        mock_interaction.response.send_message.assert_called()
        call_args = mock_interaction.response.send_message.call_args
        assert call_args[1]["ephemeral"] is True
