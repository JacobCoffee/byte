"""Tests for Litestar custom plugin commands."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from dateutil.zoneinfo import gettz
from discord import EntityType, Object, PrivacyLevel
from discord.ext.commands import Bot, Context

from byte_bot.plugins.custom.litestar import GitHubIssue, LitestarCommands

if TYPE_CHECKING:
    from discord import Guild, Interaction, Message

__all__ = ("TestGitHubIssue", "TestLitestarCommands")


class TestGitHubIssue:
    """Tests for GitHubIssue modal."""

    @pytest.fixture
    async def github_issue_modal(self) -> GitHubIssue:
        """Create GitHubIssue modal."""
        # Use MagicMock to bypass discord.py's event loop initialization
        with patch("discord.ui.modal.Modal.__init__", return_value=None):
            modal = GitHubIssue()
            # Manually set the attributes after bypass
            modal.jump_url = None
            return modal

    @pytest.fixture
    async def github_issue_modal_with_message(self, mock_message: Message) -> GitHubIssue:
        """Create GitHubIssue modal with message."""
        mock_message.content = "This is a test bug report"
        with patch("discord.ui.modal.Modal.__init__", return_value=None):
            return GitHubIssue(message=mock_message)

    async def test_modal_initialization_without_message(self) -> None:
        """Test modal initializes without message."""
        with patch("discord.ui.modal.Modal.__init__", return_value=None):
            modal = GitHubIssue()
            modal.jump_url = None

            # Check that fields exist (they are class attributes)
            assert hasattr(GitHubIssue, "title_")
            assert hasattr(GitHubIssue, "description")
            assert hasattr(GitHubIssue, "mcve")
            assert hasattr(GitHubIssue, "logs")
            assert hasattr(GitHubIssue, "version")
            assert modal.jump_url is None

    async def test_modal_initialization_with_message(self, mock_message: Message) -> None:
        """Test modal initializes with message."""
        mock_message.content = "This is a test bug report"
        with patch("discord.ui.modal.Modal.__init__", return_value=None):
            modal = GitHubIssue(message=mock_message)

            # Check description default was set
            assert GitHubIssue.description.default == mock_message.content
            assert modal.jump_url == mock_message.jump_url

    async def test_modal_on_submit_disabled(self, mock_interaction: Interaction) -> None:
        """Test modal submission during migration (disabled)."""
        with patch("discord.ui.modal.Modal.__init__", return_value=None):
            modal = GitHubIssue()
            modal.title_ = MagicMock()
            modal.title_.value = "Test Issue"
            modal.description = MagicMock()
            modal.description.value = "Test description"
            modal.mcve = MagicMock()
            modal.mcve.value = "Test MCVE"
            modal.logs = MagicMock()
            modal.logs.value = "Test logs"
            modal.version = MagicMock()
            modal.version.value = "2.0.0"

            await modal.on_submit(mock_interaction)

            mock_interaction.response.send_message.assert_called_once()
            call_args = mock_interaction.response.send_message.call_args
            assert "temporarily disabled" in call_args[0][0]
            assert call_args[1]["ephemeral"] is True

    async def test_modal_on_submit_exception_handling(self, mock_interaction: Interaction) -> None:
        """Test modal handles exceptions during submission."""
        # First call raises exception, second call (in except block) succeeds
        mock_interaction.response.send_message = AsyncMock(side_effect=[Exception("Test error"), None])

        with patch("discord.ui.modal.Modal.__init__", return_value=None):
            modal = GitHubIssue()
            modal.title_ = MagicMock()
            modal.title_.value = "Test Issue"
            modal.description = MagicMock()
            modal.description.value = "Test description"
            modal.mcve = MagicMock()
            modal.mcve.value = "Test MCVE"
            modal.logs = MagicMock()
            modal.logs.value = "Test logs"
            modal.version = MagicMock()
            modal.version.value = "2.0.0"

            # Should not raise exception
            await modal.on_submit(mock_interaction)

            # Verify exception handler was called
            assert mock_interaction.response.send_message.call_count == 2
            # Second call should be the error message
            second_call_args = mock_interaction.response.send_message.call_args_list[1]
            assert "An error occurred:" in second_call_args[0][0]


class TestLitestarCommands:
    """Tests for LitestarCommands cog."""

    @pytest.fixture
    def bot(self, mock_bot: Bot) -> Bot:
        """Create mock bot."""
        mock_bot.is_owner = AsyncMock(return_value=True)
        mock_bot.add_cog = AsyncMock()
        return mock_bot

    @pytest.fixture
    def cog(self, bot: Bot) -> LitestarCommands:
        """Create LitestarCommands cog."""
        return LitestarCommands(bot)

    @pytest.fixture
    def mock_context_with_byte_dev(self, mock_context: Context, mock_member) -> Context:
        """Create mock context with byte-dev role."""
        byte_dev_role = MagicMock()
        byte_dev_role.name = "byte-dev"
        mock_member.roles = [byte_dev_role]
        mock_context.guild.get_member = MagicMock(return_value=mock_member)
        return mock_context

    @pytest.fixture
    def mock_guild_with_events(self, mock_guild: Guild) -> Guild:
        """Create mock guild with scheduled events."""
        mock_guild.scheduled_events = []
        mock_guild.create_scheduled_event = AsyncMock()
        return mock_guild

    def test_cog_initialization(self, cog: LitestarCommands, bot: Bot) -> None:
        """Test cog initializes correctly."""
        assert cog.bot == bot
        assert cog.__cog_name__ == "Litestar Commands"

    async def test_litestar_group_no_subcommand(
        self, cog: LitestarCommands, mock_context_with_byte_dev: Context
    ) -> None:
        """Test litestar group command with no subcommand."""
        mock_context_with_byte_dev.invoked_subcommand = None
        mock_context_with_byte_dev.send = AsyncMock()
        mock_context_with_byte_dev.send_help = AsyncMock()
        mock_context_with_byte_dev.command = MagicMock()

        # Call the underlying method directly
        await cog.litestar.callback(cog, mock_context_with_byte_dev)

        mock_context_with_byte_dev.send.assert_called_once()
        call_args = mock_context_with_byte_dev.send.call_args[0][0]
        assert "Invalid Litestar command" in call_args
        mock_context_with_byte_dev.send_help.assert_called_once()

    async def test_apply_role_embed_creates_embed(self, cog: LitestarCommands, mock_context: Context) -> None:
        """Test apply_role_embed creates and sends correct embed."""
        mock_context.send = AsyncMock()
        mock_context.bot.is_owner = AsyncMock(return_value=True)

        await cog.apply_role_embed.callback(cog, mock_context)

        mock_context.send.assert_called_once()
        embed_arg = mock_context.send.call_args[1]["embed"]
        assert embed_arg.title == "Litestar Roles"
        assert len(embed_arg.fields) > 0

    async def test_apply_role_embed_has_organization_roles(self, cog: LitestarCommands, mock_context: Context) -> None:
        """Test apply_role_embed includes organization roles section."""
        mock_context.send = AsyncMock()
        mock_context.bot.is_owner = AsyncMock(return_value=True)

        await cog.apply_role_embed.callback(cog, mock_context)

        embed_arg = mock_context.send.call_args[1]["embed"]
        field_names = [field.name for field in embed_arg.fields]
        assert "Organization Roles" in field_names

    async def test_apply_role_embed_has_community_roles(self, cog: LitestarCommands, mock_context: Context) -> None:
        """Test apply_role_embed includes community roles section."""
        mock_context.send = AsyncMock()
        mock_context.bot.is_owner = AsyncMock(return_value=True)

        await cog.apply_role_embed.callback(cog, mock_context)

        embed_arg = mock_context.send.call_args[1]["embed"]
        field_names = [field.name for field in embed_arg.fields]
        assert "Community Roles" in field_names

    @patch("byte_bot.plugins.custom.litestar.get_next_friday")
    async def test_schedule_office_hours_success(
        self, mock_get_next_friday, cog: LitestarCommands, mock_interaction: Interaction, mock_guild_with_events: Guild
    ) -> None:
        """Test scheduling office hours successfully."""
        # Mock the next Friday calculation
        now = datetime.datetime.now(gettz("America/Chicago"))
        start_dt = now.replace(hour=11, minute=0, second=0, microsecond=0)
        end_dt = start_dt + datetime.timedelta(hours=1)
        mock_get_next_friday.return_value = (start_dt, end_dt)

        mock_interaction.guild = mock_guild_with_events

        await cog.schedule_office_hours.callback(cog, mock_interaction, None)

        mock_guild_with_events.create_scheduled_event.assert_called_once()
        call_kwargs = mock_guild_with_events.create_scheduled_event.call_args[1]
        assert call_kwargs["name"] == "Office Hours"
        assert call_kwargs["entity_type"] == EntityType.stage_instance
        assert call_kwargs["privacy_level"] == PrivacyLevel.guild_only

        mock_interaction.response.send_message.assert_called_once()
        response_message = mock_interaction.response.send_message.call_args[0][0]
        assert "Office Hours event scheduled" in response_message

    @patch("byte_bot.plugins.custom.litestar.get_next_friday")
    async def test_schedule_office_hours_with_delay(
        self, mock_get_next_friday, cog: LitestarCommands, mock_interaction: Interaction, mock_guild_with_events: Guild
    ) -> None:
        """Test scheduling office hours with delay parameter."""
        now = datetime.datetime.now(gettz("America/Chicago"))
        start_dt = now.replace(hour=11, minute=0, second=0, microsecond=0) + datetime.timedelta(weeks=2)
        end_dt = start_dt + datetime.timedelta(hours=1)
        mock_get_next_friday.return_value = (start_dt, end_dt)

        mock_interaction.guild = mock_guild_with_events

        await cog.schedule_office_hours.callback(cog, mock_interaction, 2)

        mock_get_next_friday.assert_called_once()
        mock_guild_with_events.create_scheduled_event.assert_called_once()

    async def test_schedule_office_hours_no_guild(self, cog: LitestarCommands, mock_interaction: Interaction) -> None:
        """Test scheduling office hours without guild context."""
        mock_interaction.guild = None

        await cog.schedule_office_hours.callback(cog, mock_interaction, None)

        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert "only be used in a guild" in call_args[0][0]
        assert call_args[1]["ephemeral"] is True

    @patch("byte_bot.plugins.custom.litestar.get_next_friday")
    async def test_schedule_office_hours_duplicate_event(
        self, mock_get_next_friday, cog: LitestarCommands, mock_interaction: Interaction, mock_guild_with_events: Guild
    ) -> None:
        """Test scheduling office hours when event already exists."""
        # Mock the next Friday calculation
        now = datetime.datetime.now(gettz("America/Chicago"))
        start_dt = now.replace(hour=11, minute=0, second=0, microsecond=0)
        end_dt = start_dt + datetime.timedelta(hours=1)
        mock_get_next_friday.return_value = (start_dt, end_dt)

        # Create existing event
        existing_event = MagicMock()
        existing_event.name = "Office Hours"
        # Mock the start_time with proper astimezone behavior
        mock_start_time = MagicMock()
        mock_astimezone_result = MagicMock()
        mock_astimezone_result.date.return_value = start_dt.date()
        mock_start_time.astimezone.return_value = mock_astimezone_result
        existing_event.start_time = mock_start_time

        mock_guild_with_events.scheduled_events = [existing_event]
        mock_interaction.guild = mock_guild_with_events

        await cog.schedule_office_hours.callback(cog, mock_interaction, None)

        # Should not create new event
        mock_guild_with_events.create_scheduled_event.assert_not_called()

        # Should send error message
        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert "already scheduled" in call_args[0][0]
        assert call_args[1]["ephemeral"] is True

    @patch("byte_bot.plugins.custom.litestar.get_next_friday")
    async def test_schedule_office_hours_uses_correct_channel(
        self, mock_get_next_friday, cog: LitestarCommands, mock_interaction: Interaction, mock_guild_with_events: Guild
    ) -> None:
        """Test office hours uses correct stage channel."""
        now = datetime.datetime.now(gettz("America/Chicago"))
        start_dt = now.replace(hour=11, minute=0, second=0, microsecond=0)
        end_dt = start_dt + datetime.timedelta(hours=1)
        mock_get_next_friday.return_value = (start_dt, end_dt)

        mock_interaction.guild = mock_guild_with_events

        await cog.schedule_office_hours.callback(cog, mock_interaction, None)

        call_kwargs = mock_guild_with_events.create_scheduled_event.call_args[1]
        assert isinstance(call_kwargs["channel"], Object)
        assert call_kwargs["channel"].id == 1215926860144443502  # Expected stage channel ID

    @patch("byte_bot.plugins.custom.litestar.get_next_friday")
    async def test_schedule_office_hours_includes_reason(
        self, mock_get_next_friday, cog: LitestarCommands, mock_interaction: Interaction, mock_guild_with_events: Guild
    ) -> None:
        """Test office hours includes audit log reason."""
        now = datetime.datetime.now(gettz("America/Chicago"))
        start_dt = now.replace(hour=11, minute=0, second=0, microsecond=0)
        end_dt = start_dt + datetime.timedelta(hours=1)
        mock_get_next_friday.return_value = (start_dt, end_dt)

        mock_interaction.guild = mock_guild_with_events
        mock_interaction.user.name = "TestUser"

        await cog.schedule_office_hours.callback(cog, mock_interaction, None)

        call_kwargs = mock_guild_with_events.create_scheduled_event.call_args[1]
        assert "reason" in call_kwargs
        assert "Scheduled by" in call_kwargs["reason"]
        assert "/schedule-office-hours" in call_kwargs["reason"]

    async def test_setup_adds_cog(self, bot: Bot) -> None:
        """Test setup function adds cog to bot."""
        from byte_bot.plugins.custom.litestar import setup

        await setup(bot)

        bot.add_cog.assert_called_once()
        added_cog = bot.add_cog.call_args[0][0]
        assert isinstance(added_cog, LitestarCommands)
        assert added_cog.bot == bot

    def test_cog_has_expected_commands(self, cog: LitestarCommands) -> None:
        """Test cog has all expected commands."""
        # Check for command methods
        assert hasattr(cog, "litestar")
        assert hasattr(cog, "apply_role_embed")
        assert hasattr(cog, "schedule_office_hours")

        # Verify they are callable
        assert callable(cog.litestar.callback)
        assert callable(cog.apply_role_embed.callback)
        assert callable(cog.schedule_office_hours.callback)

    async def test_litestar_group_with_subcommand(
        self, cog: LitestarCommands, mock_context_with_byte_dev: Context
    ) -> None:
        """Test litestar group command with subcommand invoked."""
        mock_context_with_byte_dev.invoked_subcommand = "some_subcommand"
        mock_context_with_byte_dev.send = AsyncMock()
        mock_context_with_byte_dev.send_help = AsyncMock()

        # Call the underlying method directly
        await cog.litestar.callback(cog, mock_context_with_byte_dev)

        # Should not send help when subcommand is present
        mock_context_with_byte_dev.send.assert_not_called()
        mock_context_with_byte_dev.send_help.assert_not_called()

    async def test_modal_fields_configuration(self) -> None:
        """Test modal fields are properly configured."""
        # Verify field configurations
        assert GitHubIssue.title_.label == "title"
        assert GitHubIssue.description.label == "Description"
        assert GitHubIssue.mcve.label == "MCVE"
        assert GitHubIssue.logs.label == "Logs"
        assert GitHubIssue.version.label == "Litestar Version"

    @patch("byte_bot.plugins.custom.litestar.get_next_friday")
    async def test_schedule_office_hours_different_existing_event(
        self, mock_get_next_friday, cog: LitestarCommands, mock_interaction: Interaction, mock_guild_with_events: Guild
    ) -> None:
        """Test scheduling office hours when different event exists on same day."""
        # Mock the next Friday calculation
        now = datetime.datetime.now(gettz("America/Chicago"))
        start_dt = now.replace(hour=11, minute=0, second=0, microsecond=0)
        end_dt = start_dt + datetime.timedelta(hours=1)
        mock_get_next_friday.return_value = (start_dt, end_dt)

        # Create existing event with different name
        existing_event = MagicMock()
        existing_event.name = "Different Event"
        mock_start_time = MagicMock()
        mock_astimezone_result = MagicMock()
        mock_astimezone_result.date.return_value = start_dt.date()
        mock_start_time.astimezone.return_value = mock_astimezone_result
        existing_event.start_time = mock_start_time

        mock_guild_with_events.scheduled_events = [existing_event]
        mock_interaction.guild = mock_guild_with_events

        await cog.schedule_office_hours.callback(cog, mock_interaction, None)

        # Should create new event since existing event has different name
        mock_guild_with_events.create_scheduled_event.assert_called_once()

    @patch("byte_bot.plugins.custom.litestar.get_next_friday")
    async def test_schedule_office_hours_different_date(
        self, mock_get_next_friday, cog: LitestarCommands, mock_interaction: Interaction, mock_guild_with_events: Guild
    ) -> None:
        """Test scheduling office hours when Office Hours exists on different date."""
        # Mock the next Friday calculation
        now = datetime.datetime.now(gettz("America/Chicago"))
        start_dt = now.replace(hour=11, minute=0, second=0, microsecond=0)
        end_dt = start_dt + datetime.timedelta(hours=1)
        mock_get_next_friday.return_value = (start_dt, end_dt)

        # Create existing event on different date
        existing_event = MagicMock()
        existing_event.name = "Office Hours"
        mock_start_time = MagicMock()
        mock_astimezone_result = MagicMock()
        different_date = start_dt.date() - datetime.timedelta(days=7)
        mock_astimezone_result.date.return_value = different_date
        mock_start_time.astimezone.return_value = mock_astimezone_result
        existing_event.start_time = mock_start_time

        mock_guild_with_events.scheduled_events = [existing_event]
        mock_interaction.guild = mock_guild_with_events

        await cog.schedule_office_hours.callback(cog, mock_interaction, None)

        # Should create new event since dates are different
        mock_guild_with_events.create_scheduled_event.assert_called_once()
