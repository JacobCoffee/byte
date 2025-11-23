"""Tests for Byte bot lifecycle and core functionality."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from discord import Activity, Embed, Forbidden, Intents, NotFound
from discord.ext.commands import CommandError, Context
from httpx import ConnectError

from byte_bot.bot import Byte

if TYPE_CHECKING:
    from discord import Guild, Member, Message


class TestByteInitialization:
    """Tests for Byte bot initialization."""

    def test_bot_initialization(self) -> None:
        """Test bot initializes with correct parameters."""
        intents = Intents.default()
        activity = Activity(name="test")
        prefix = ["!", "?"]

        bot = Byte(command_prefix=prefix, intents=intents, activity=activity)

        assert bot.command_prefix == prefix
        assert bot.intents == intents
        # Compare activity by name since Activity objects don't compare by value
        assert bot.activity.name == activity.name

    def test_bot_inherits_from_bot(self) -> None:
        """Test Byte inherits from discord.ext.commands.Bot."""
        from discord.ext.commands import Bot as DiscordBot

        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        assert isinstance(bot, DiscordBot)


class TestSetupHook:
    """Tests for setup_hook method."""

    @pytest.mark.asyncio
    async def test_setup_hook_loads_cogs(self) -> None:
        """Test setup_hook loads cogs."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        with (
            patch.object(bot, "load_cogs", new=AsyncMock()) as mock_load_cogs,
            patch("byte_bot.bot.bot_settings") as mock_settings,
        ):
            mock_settings.discord_dev_guild_id = None
            await bot.setup_hook()

            mock_load_cogs.assert_called_once()

    @pytest.mark.asyncio
    async def test_setup_hook_syncs_dev_guild(self) -> None:
        """Test setup_hook syncs tree to dev guild if configured."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.tree.sync = AsyncMock()
        bot.tree.copy_global_to = MagicMock()

        with (
            patch.object(bot, "load_cogs", new=AsyncMock()),
            patch("byte_bot.bot.bot_settings") as mock_settings,
        ):
            mock_settings.discord_dev_guild_id = 123456789
            await bot.setup_hook()

            bot.tree.copy_global_to.assert_called_once()
            bot.tree.sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_setup_hook_no_dev_guild(self) -> None:
        """Test setup_hook skips sync if no dev guild configured."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.tree.sync = AsyncMock()
        bot.tree.copy_global_to = MagicMock()

        with (
            patch.object(bot, "load_cogs", new=AsyncMock()),
            patch("byte_bot.bot.bot_settings") as mock_settings,
        ):
            mock_settings.discord_dev_guild_id = None
            await bot.setup_hook()

            bot.tree.copy_global_to.assert_not_called()
            bot.tree.sync.assert_not_called()


class TestLoadCogs:
    """Tests for load_cogs method."""

    @pytest.mark.asyncio
    async def test_load_cogs_discovers_plugins(self, tmp_path: Path) -> None:
        """Test load_cogs discovers and loads plugin files."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.load_extension = AsyncMock()

        # Create mock plugin directory
        plugins_dir = tmp_path / "byte_bot" / "plugins"
        plugins_dir.mkdir(parents=True)
        (plugins_dir / "test_plugin.py").touch()
        (plugins_dir / "another_plugin.py").touch()
        (plugins_dir / "__init__.py").touch()  # Should be skipped

        with patch("byte_bot.bot.bot_settings") as mock_settings:
            mock_settings.plugins_dir = plugins_dir
            await bot.load_cogs()

            # Should load 2 plugins (excluding __init__.py)
            assert bot.load_extension.call_count == 2

    @pytest.mark.asyncio
    async def test_load_cogs_skips_init_files(self, tmp_path: Path) -> None:
        """Test load_cogs skips __init__.py files."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.load_extension = AsyncMock()

        plugins_dir = tmp_path / "byte_bot" / "plugins"
        plugins_dir.mkdir(parents=True)
        (plugins_dir / "__init__.py").touch()

        with patch("byte_bot.bot.bot_settings") as mock_settings:
            mock_settings.plugins_dir = plugins_dir
            await bot.load_cogs()

            bot.load_extension.assert_not_called()

    @pytest.mark.asyncio
    async def test_load_cogs_handles_already_loaded(self, tmp_path: Path) -> None:
        """Test load_cogs handles ExtensionAlreadyLoaded gracefully."""
        from discord.ext.commands import ExtensionAlreadyLoaded

        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.load_extension = AsyncMock(side_effect=ExtensionAlreadyLoaded("test"))

        plugins_dir = tmp_path / "byte_bot" / "plugins"
        plugins_dir.mkdir(parents=True)
        (plugins_dir / "test_plugin.py").touch()

        with patch("byte_bot.bot.bot_settings") as mock_settings:
            mock_settings.plugins_dir = plugins_dir
            # Should not raise exception
            await bot.load_cogs()

    @pytest.mark.asyncio
    async def test_load_cogs_handles_missing_directory(self, tmp_path: Path) -> None:
        """Test load_cogs handles missing plugins directory."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.load_extension = AsyncMock()

        plugins_dir = tmp_path / "nonexistent" / "plugins"

        with patch("byte_bot.bot.bot_settings") as mock_settings:
            mock_settings.plugins_dir = plugins_dir
            # Should not raise exception
            await bot.load_cogs()

            bot.load_extension.assert_not_called()

    @pytest.mark.asyncio
    async def test_load_cogs_recursive_discovery(self, tmp_path: Path) -> None:
        """Test load_cogs discovers plugins in subdirectories."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.load_extension = AsyncMock()

        plugins_dir = tmp_path / "byte_bot" / "plugins"
        plugins_dir.mkdir(parents=True)
        (plugins_dir / "top_level.py").touch()

        subdir = plugins_dir / "custom"
        subdir.mkdir()
        (subdir / "nested_plugin.py").touch()

        with patch("byte_bot.bot.bot_settings") as mock_settings:
            mock_settings.plugins_dir = plugins_dir
            await bot.load_cogs()

            # Should load both top-level and nested plugins
            assert bot.load_extension.call_count == 2


class TestOnReady:
    """Tests for on_ready event handler."""

    @pytest.mark.asyncio
    async def test_on_ready_logs_connection(self) -> None:
        """Test on_ready logs bot connection."""
        from unittest.mock import PropertyMock

        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        # Mock user property
        mock_user = MagicMock()
        mock_user.name = "ByteBot"
        type(bot).user = PropertyMock(return_value=mock_user)

        with patch("byte_bot.bot.logger") as mock_logger:
            await bot.on_ready()

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0]
            assert "connected" in call_args[0].lower()


class TestOnMessage:
    """Tests for on_message event handler."""

    @pytest.mark.asyncio
    async def test_on_message_processes_commands(self, mock_message: Message) -> None:
        """Test on_message processes commands."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.process_commands = AsyncMock()

        await bot.on_message(mock_message)

        bot.process_commands.assert_called_once_with(mock_message)


class TestOnCommandError:
    """Tests for on_command_error event handler."""

    @pytest.fixture
    def bot(self) -> Byte:
        """Create bot instance."""
        intents = Intents.default()
        activity = Activity(name="test")
        return Byte(command_prefix=["!"], intents=intents, activity=activity)

    @pytest.fixture
    def context(self, mock_context: Context) -> Context:
        """Create context with all required attributes."""
        mock_context.author.avatar = MagicMock()
        mock_context.author.avatar.url = "https://example.com/avatar.png"
        mock_context.guild.name = "Test Guild"
        mock_context.channel.mention = "<#123456>"
        mock_context.author.mention = "<@987654>"
        mock_context.message.jump_url = "https://discord.com/channels/123/456/789"
        mock_context.message.created_at.strftime = MagicMock(return_value="2024-01-01 12:00:00")
        mock_context.interaction = None
        mock_context.send = AsyncMock()
        return mock_context

    @pytest.mark.asyncio
    async def test_on_command_error_ignores_forbidden(self, bot: Byte, context: Context) -> None:
        """Test on_command_error ignores Forbidden errors."""
        error = CommandError("Test")
        error.original = Forbidden(MagicMock(), "Forbidden")  # type: ignore[attr-defined]

        await bot.on_command_error(context, error)

        context.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_command_error_ignores_not_found(self, bot: Byte, context: Context) -> None:
        """Test on_command_error ignores NotFound errors."""
        error = CommandError("Test")
        error.original = NotFound(MagicMock(), "Not found")  # type: ignore[attr-defined]

        await bot.on_command_error(context, error)

        context.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_command_error_sends_embed(self, bot: Byte, context: Context) -> None:
        """Test on_command_error sends error embed."""
        error = CommandError("Test error message")

        await bot.on_command_error(context, error)

        context.send.assert_called_once()
        call_args = context.send.call_args
        assert "embed" in call_args[1]
        embed = call_args[1]["embed"]
        assert embed.title == "Command Error"
        assert "Test error message" in embed.description

    @pytest.mark.asyncio
    async def test_on_command_error_embed_fields(self, bot: Byte, context: Context) -> None:
        """Test error embed contains all required fields."""
        error = CommandError("Test error")
        context.command.name = "testcommand"

        await bot.on_command_error(context, error)

        embed = context.send.call_args[1]["embed"]
        field_names = [f.name for f in embed.fields]
        assert "Command" in field_names
        assert "Message" in field_names
        assert "Channel" in field_names
        assert "Author" in field_names
        assert "Guild" in field_names
        assert "Location" in field_names

    @pytest.mark.asyncio
    async def test_on_command_error_dm_context(self, bot: Byte, context: Context) -> None:
        """Test error handler works in DM context."""
        error = CommandError("Test error")
        context.guild = None

        await bot.on_command_error(context, error)

        embed = context.send.call_args[1]["embed"]
        # Find the Guild field
        guild_field = next(f for f in embed.fields if f.name == "Guild")
        assert guild_field.value == "DM"

    @pytest.mark.asyncio
    async def test_on_command_error_with_interaction(self, bot: Byte, context: Context) -> None:
        """Test error handler uses interaction response if available."""
        error = CommandError("Test error")
        context.interaction = MagicMock()
        context.interaction.response.send_message = AsyncMock()

        await bot.on_command_error(context, error)

        context.interaction.response.send_message.assert_called_once()
        call_args = context.interaction.response.send_message.call_args
        assert call_args[1]["ephemeral"] is True

    @pytest.mark.asyncio
    async def test_on_command_error_without_avatar(self, bot: Byte, context: Context) -> None:
        """Test error handler works when user has no avatar."""
        error = CommandError("Test error")
        context.author.avatar = None

        await bot.on_command_error(context, error)

        embed = context.send.call_args[1]["embed"]
        # Should not set thumbnail
        assert embed.thumbnail.url is None or embed.thumbnail == Embed.Empty


class TestOnMemberJoin:
    """Tests for on_member_join event handler."""

    @pytest.mark.asyncio
    async def test_on_member_join_sends_welcome_message(self, mock_member: Member) -> None:
        """Test on_member_join sends welcome message to non-bot members."""
        mock_member.bot = False
        mock_member.send = AsyncMock()
        mock_member.guild.name = "Test Guild"

        await Byte.on_member_join(mock_member)

        mock_member.send.assert_called_once()
        call_args = mock_member.send.call_args[0][0]
        assert "Welcome" in call_args
        assert "Test Guild" in call_args

    @pytest.mark.asyncio
    async def test_on_member_join_ignores_bots(self, mock_member: Member) -> None:
        """Test on_member_join ignores bot members."""
        mock_member.bot = True
        mock_member.send = AsyncMock()

        await Byte.on_member_join(mock_member)

        mock_member.send.assert_not_called()


class TestOnGuildJoin:
    """Tests for on_guild_join event handler."""

    @pytest.mark.asyncio
    async def test_on_guild_join_syncs_tree(self, mock_guild: Guild) -> None:
        """Test on_guild_join syncs command tree."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.tree.sync = AsyncMock()

        with (
            patch("byte_bot.bot.bot_settings") as mock_settings,
            patch("httpx.AsyncClient") as mock_client,
        ):
            mock_settings.api_service_url = "http://localhost:8000"
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            await bot.on_guild_join(mock_guild)

            bot.tree.sync.assert_called_once_with(guild=mock_guild)

    @pytest.mark.asyncio
    async def test_on_guild_join_creates_guild_in_api(self, mock_guild: Guild) -> None:
        """Test on_guild_join creates guild record in API."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.tree.sync = AsyncMock()

        with (
            patch("byte_bot.bot.bot_settings") as mock_settings,
            patch("httpx.AsyncClient") as mock_client_class,
        ):
            mock_settings.api_service_url = "http://localhost:8000"
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            await bot.on_guild_join(mock_guild)

            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args[0][0]
            assert "/api/guilds/create" in call_args
            assert str(mock_guild.id) in call_args
            assert mock_guild.name in call_args

    @pytest.mark.asyncio
    async def test_on_guild_join_handles_api_failure(self, mock_guild: Guild) -> None:
        """Test on_guild_join handles API failure gracefully."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.tree.sync = AsyncMock()

        with (
            patch("byte_bot.bot.bot_settings") as mock_settings,
            patch("httpx.AsyncClient") as mock_client_class,
            patch("byte_bot.bot.logger") as mock_logger,
        ):
            mock_settings.api_service_url = "http://localhost:8000"
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Should not raise exception
            await bot.on_guild_join(mock_guild)

            mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_on_guild_join_handles_connection_error(self, mock_guild: Guild) -> None:
        """Test on_guild_join handles connection errors."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.tree.sync = AsyncMock()

        with (
            patch("byte_bot.bot.bot_settings") as mock_settings,
            patch("httpx.AsyncClient") as mock_client_class,
            patch("byte_bot.bot.logger") as mock_logger,
        ):
            mock_settings.api_service_url = "http://localhost:8000"
            mock_client_class.return_value.__aenter__.side_effect = ConnectError("Connection refused")

            # Should not raise exception
            await bot.on_guild_join(mock_guild)

            mock_logger.exception.assert_called()


class TestRunBot:
    """Tests for run_bot function."""

    @patch("byte_bot.bot.run")
    @patch("byte_bot.bot.Byte")
    def test_run_bot_creates_bot_with_intents(self, mock_byte_class: MagicMock, mock_run: MagicMock) -> None:
        """Test run_bot creates bot with correct intents."""
        from byte_bot.bot import run_bot

        with patch("byte_bot.bot.bot_settings") as mock_settings:
            mock_settings.command_prefix = ["!"]
            mock_settings.presence_url = "https://example.com"
            mock_settings.discord_token = "test_token"

            run_bot()

            # Check bot was created
            mock_byte_class.assert_called_once()
            call_kwargs = mock_byte_class.call_args[1]

            # Check intents
            intents = call_kwargs["intents"]
            assert intents.message_content is True
            assert intents.members is True

    @patch("byte_bot.bot.run")
    @patch("byte_bot.bot.Byte")
    def test_run_bot_sets_activity(self, mock_byte_class: MagicMock, mock_run: MagicMock) -> None:
        """Test run_bot sets bot activity."""
        from byte_bot.bot import run_bot

        with patch("byte_bot.bot.bot_settings") as mock_settings:
            mock_settings.command_prefix = ["!"]
            mock_settings.presence_url = "https://example.com"
            mock_settings.discord_token = "test_token"

            run_bot()

            call_kwargs = mock_byte_class.call_args[1]
            activity = call_kwargs["activity"]
            assert activity.name == "!help"
            assert activity.state == "Serving Developers"

    @patch("byte_bot.bot.run")
    @patch("byte_bot.bot.Byte")
    def test_run_bot_calls_anyio_run(self, mock_byte_class: MagicMock, mock_run: MagicMock) -> None:
        """Test run_bot calls anyio.run with start_bot coroutine."""
        from byte_bot.bot import run_bot

        mock_bot_instance = MagicMock()
        mock_bot_instance.start = AsyncMock()
        mock_byte_class.return_value = mock_bot_instance

        with patch("byte_bot.bot.bot_settings") as mock_settings:
            mock_settings.command_prefix = ["!"]
            mock_settings.presence_url = "https://example.com"
            mock_settings.discord_token = "test_token"

            run_bot()

            # Verify anyio.run was called
            mock_run.assert_called_once()

    @patch("byte_bot.bot.run")
    @patch("byte_bot.bot.Byte")
    def test_run_bot_start_bot_coroutine(self, mock_byte_class: MagicMock, mock_run: MagicMock) -> None:
        """Test the start_bot coroutine calls bot.start with token."""
        import asyncio

        from byte_bot.bot import run_bot

        mock_bot_instance = MagicMock()
        mock_bot_instance.start = AsyncMock()
        mock_byte_class.return_value = mock_bot_instance

        # Capture and execute the async function passed to anyio.run
        def execute_run(async_func):
            # Call the async function to get a coroutine, then run it
            asyncio.run(async_func())

        mock_run.side_effect = execute_run

        with patch("byte_bot.bot.bot_settings") as mock_settings:
            mock_settings.command_prefix = ["!"]
            mock_settings.presence_url = "https://example.com"
            mock_settings.discord_token = "test_token_123"

            run_bot()

            # Verify bot.start was called with the token
            mock_bot_instance.start.assert_called_once_with("test_token_123")


class TestEdgeCases:
    """Additional edge case tests for full coverage."""

    @pytest.mark.asyncio
    async def test_setup_hook_tree_sync_failure(self) -> None:
        """Test setup_hook handles tree sync failures gracefully."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.tree.sync = AsyncMock(side_effect=Exception("Sync failed"))
        bot.tree.copy_global_to = MagicMock()

        with (
            patch.object(bot, "load_cogs", new=AsyncMock()),
            patch("byte_bot.bot.bot_settings") as mock_settings,
        ):
            mock_settings.discord_dev_guild_id = 123456789

            # Should raise exception from sync
            with pytest.raises(Exception, match="Sync failed"):
                await bot.setup_hook()

    @pytest.mark.asyncio
    async def test_load_cogs_other_exception_propagates(self, tmp_path: Path) -> None:
        """Test load_cogs propagates non-ExtensionAlreadyLoaded exceptions."""
        from discord.ext.commands import ExtensionFailed

        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.load_extension = AsyncMock(side_effect=ExtensionFailed("test", Exception("Test error")))

        plugins_dir = tmp_path / "byte_bot" / "plugins"
        plugins_dir.mkdir(parents=True)
        (plugins_dir / "test_plugin.py").touch()

        with patch("byte_bot.bot.bot_settings") as mock_settings:
            mock_settings.plugins_dir = plugins_dir

            # Should raise exception
            with pytest.raises(ExtensionFailed):
                await bot.load_cogs()

    @pytest.mark.asyncio
    async def test_on_message_with_bot_author(self, mock_message: Message) -> None:
        """Test on_message processes messages from bot users."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.process_commands = AsyncMock()

        # Bot messages are still processed (bot doesn't filter them out)
        mock_message.author.bot = True

        await bot.on_message(mock_message)

        # Should still call process_commands (filtering happens in command handler)
        bot.process_commands.assert_called_once_with(mock_message)

    @pytest.mark.asyncio
    async def test_on_command_error_with_nested_original_error(self) -> None:
        """Test on_command_error handles nested original errors."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        # Create context
        context = MagicMock(spec=Context)
        context.author = MagicMock()
        context.author.avatar = MagicMock()
        context.author.avatar.url = "https://example.com/avatar.png"
        context.author.mention = "<@123>"
        context.guild = MagicMock()
        context.guild.name = "Test Guild"
        context.channel = MagicMock()
        context.channel.mention = "<#456>"
        context.message = MagicMock()
        context.message.content = "!test command"
        context.message.jump_url = "https://discord.com/channels/1/2/3"
        context.message.created_at = MagicMock()
        context.message.created_at.strftime = MagicMock(return_value="2024-01-01 12:00:00")
        context.command = MagicMock()
        context.command.name = "test"
        context.interaction = None
        context.send = AsyncMock()

        # Create error with nested original that is Forbidden
        error = CommandError("Test error")
        inner_error = Forbidden(MagicMock(), "Forbidden")
        error.original = inner_error  # type: ignore[attr-defined]

        await bot.on_command_error(context, error)

        # Should be ignored due to Forbidden
        context.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_command_error_channel_without_mention(self) -> None:
        """Test on_command_error handles channels without mention attribute."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        # Create context with channel that doesn't have mention
        context = MagicMock(spec=Context)
        context.author = MagicMock()
        context.author.avatar = None
        context.author.mention = "<@123>"
        context.guild = MagicMock()
        context.guild.name = "Test Guild"
        context.channel = "dm-channel"  # String instead of channel object
        context.message = MagicMock()
        context.message.content = "!test"
        context.message.jump_url = "https://discord.com/channels/1/2/3"
        context.message.created_at = MagicMock()
        context.message.created_at.strftime = MagicMock(return_value="2024-01-01 12:00:00")
        context.command = MagicMock()
        context.command.name = "test"
        context.interaction = None
        context.send = AsyncMock()

        error = CommandError("Test error")

        await bot.on_command_error(context, error)

        # Should still send embed with str(channel)
        context.send.assert_called_once()
        embed = context.send.call_args[1]["embed"]
        channel_field = next(f for f in embed.fields if f.name == "Channel")
        assert channel_field.value == "dm-channel"

    @pytest.mark.asyncio
    async def test_on_member_join_send_failure(self, mock_member: Member) -> None:
        """Test on_member_join handles send failures gracefully."""
        mock_member.bot = False
        mock_member.send = AsyncMock(side_effect=Forbidden(MagicMock(), "Cannot send messages"))
        mock_member.guild.name = "Test Guild"

        # Should raise the exception (not caught in the code)
        with pytest.raises(Forbidden):
            await Byte.on_member_join(mock_member)

    @pytest.mark.asyncio
    async def test_on_guild_join_tree_sync_failure(self, mock_guild: Guild) -> None:
        """Test on_guild_join handles tree sync failures."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.tree.sync = AsyncMock(side_effect=Exception("Sync failed"))

        with (
            patch("byte_bot.bot.bot_settings") as mock_settings,
            patch("httpx.AsyncClient"),
        ):
            mock_settings.api_service_url = "http://localhost:8000"

            # Should raise exception from tree.sync
            with pytest.raises(Exception, match="Sync failed"):
                await bot.on_guild_join(mock_guild)

    @pytest.mark.asyncio
    async def test_on_guild_join_api_non_201_status(self, mock_guild: Guild) -> None:
        """Test on_guild_join handles non-201 API responses."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.tree.sync = AsyncMock()

        with (
            patch("byte_bot.bot.bot_settings") as mock_settings,
            patch("httpx.AsyncClient") as mock_client_class,
            patch("byte_bot.bot.logger") as mock_logger,
        ):
            mock_settings.api_service_url = "http://localhost:8000"
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            await bot.on_guild_join(mock_guild)

            # Should log the failure
            assert any("Guild Join Failed" in str(call) for call in mock_logger.info.call_args_list)

    @pytest.mark.asyncio
    async def test_on_ready_with_none_user(self) -> None:
        """Test on_ready handles None user gracefully."""
        from unittest.mock import PropertyMock

        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        # Mock user property as None
        type(bot).user = PropertyMock(return_value=None)

        with patch("byte_bot.bot.logger") as mock_logger:
            await bot.on_ready()

            # Should still log (with None)
            mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_command_prefixes(self) -> None:
        """Test bot supports multiple command prefixes."""
        intents = Intents.default()
        activity = Activity(name="test")
        prefixes = ["!", "?", ">>"]

        bot = Byte(command_prefix=prefixes, intents=intents, activity=activity)

        assert bot.command_prefix == prefixes

    @pytest.mark.asyncio
    async def test_on_command_error_error_without_original(self) -> None:
        """Test on_command_error handles errors without original attribute."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        context = MagicMock(spec=Context)
        context.author = MagicMock()
        context.author.avatar = None
        context.author.mention = "<@123>"
        context.guild = MagicMock()
        context.guild.name = "Test Guild"
        context.channel = MagicMock()
        context.channel.mention = "<#456>"
        context.message = MagicMock()
        context.message.content = "!test"
        context.message.jump_url = "https://discord.com/channels/1/2/3"
        context.message.created_at = MagicMock()
        context.message.created_at.strftime = MagicMock(return_value="2024-01-01 12:00:00")
        context.command = MagicMock()
        context.command.name = "test"
        context.interaction = None
        context.send = AsyncMock()

        # Error without original attribute
        error = CommandError("Direct error")

        await bot.on_command_error(context, error)

        # Should send embed with the error message
        context.send.assert_called_once()
        embed = context.send.call_args[1]["embed"]
        assert "Direct error" in embed.description

    @pytest.mark.asyncio
    async def test_load_cogs_empty_directory(self, tmp_path: Path) -> None:
        """Test load_cogs handles empty plugins directory."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.load_extension = AsyncMock()

        plugins_dir = tmp_path / "byte_bot" / "plugins"
        plugins_dir.mkdir(parents=True)

        with patch("byte_bot.bot.bot_settings") as mock_settings:
            mock_settings.plugins_dir = plugins_dir
            await bot.load_cogs()

            # Should not attempt to load any cogs
            bot.load_extension.assert_not_called()

    @pytest.mark.asyncio
    async def test_load_cogs_complex_path_construction(self, tmp_path: Path) -> None:
        """Test load_cogs correctly constructs import paths for nested plugins."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.load_extension = AsyncMock()

        # Create deeply nested plugin
        plugins_dir = tmp_path / "byte_bot" / "plugins"
        subdir1 = plugins_dir / "feature"
        subdir2 = subdir1 / "subfeature"
        subdir2.mkdir(parents=True)
        (subdir2 / "deep_plugin.py").touch()

        with patch("byte_bot.bot.bot_settings") as mock_settings:
            mock_settings.plugins_dir = plugins_dir
            await bot.load_cogs()

            # Verify correct import path construction
            bot.load_extension.assert_called_once()
            call_arg = bot.load_extension.call_args[0][0]
            assert "byte_bot.plugins.feature.subfeature.deep_plugin" == call_arg

    @pytest.mark.asyncio
    async def test_on_guild_join_url_construction(self, mock_guild: Guild) -> None:
        """Test on_guild_join constructs correct API URL."""
        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)
        bot.tree.sync = AsyncMock()

        mock_guild.id = 999888777
        mock_guild.name = "Test Guild Name"

        with (
            patch("byte_bot.bot.bot_settings") as mock_settings,
            patch("httpx.AsyncClient") as mock_client_class,
        ):
            mock_settings.api_service_url = "http://api.example.com:8080"
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            await bot.on_guild_join(mock_guild)

            # Verify URL construction
            call_url = mock_client.post.call_args[0][0]
            assert "http://api.example.com:8080/api/guilds/create" in call_url
            assert "guild_id=999888777" in call_url
            assert "guild_name=Test Guild Name" in call_url
