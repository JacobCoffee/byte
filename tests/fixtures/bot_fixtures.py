"""Test fixtures for bot service testing."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import respx
from httpx import Response

if TYPE_CHECKING:
    from discord import Guild, Interaction, Member, Message, Role, TextChannel, User
    from discord.ext.commands import Bot, Context

__all__ = (
    "mock_api_client",
    "mock_api_responses",
    "mock_bot",
    "mock_channel",
    "mock_context",
    "mock_guild",
    "mock_interaction",
    "mock_member",
    "mock_message",
    "mock_role",
    "mock_user",
)


@pytest.fixture
def mock_bot() -> Bot:
    """Create a mock discord.ext.commands.Bot.

    Returns:
        Mock bot instance with common attributes.
    """
    bot = MagicMock()
    bot.user = MagicMock()
    bot.user.id = 123456789
    bot.user.name = "ByteBot"
    bot.user.discriminator = "0000"
    bot.is_owner = AsyncMock(return_value=False)
    bot.load_extension = AsyncMock()
    bot.tree = MagicMock()
    bot.tree.sync = AsyncMock()
    bot.tree.copy_global_to = MagicMock()
    return bot


@pytest.fixture
def mock_user() -> User:
    """Create a mock discord.User.

    Returns:
        Mock user instance.
    """
    user = MagicMock()
    user.id = 987654321
    user.name = "TestUser"
    user.discriminator = "1234"
    user.mention = "<@987654321>"
    user.avatar = MagicMock()
    user.avatar.url = "https://cdn.discordapp.com/avatars/987654321/test.png"
    user.bot = False
    return user


@pytest.fixture
def mock_role() -> Role:
    """Create a mock discord.Role.

    Returns:
        Mock role instance.
    """
    role = MagicMock()
    role.id = 111111111
    role.name = "TestRole"
    role.mention = "<@&111111111>"
    return role


@pytest.fixture
def mock_member(mock_user: User, mock_role: Role) -> Member:
    """Create a mock discord.Member.

    Args:
        mock_user: Mock user fixture
        mock_role: Mock role fixture

    Returns:
        Mock member instance.
    """
    member = MagicMock()
    member.id = mock_user.id
    member.name = mock_user.name
    member.discriminator = mock_user.discriminator
    member.mention = mock_user.mention
    member.avatar = mock_user.avatar
    member.bot = False
    member.roles = [mock_role]
    member.guild_permissions = MagicMock()
    member.guild_permissions.administrator = False
    member.send = AsyncMock()
    return member


@pytest.fixture
def mock_guild(mock_member: Member) -> Guild:
    """Create a mock discord.Guild.

    Args:
        mock_member: Mock member fixture

    Returns:
        Mock guild instance.
    """
    guild = MagicMock()
    guild.id = 555555555
    guild.name = "Test Guild"
    guild.get_member = MagicMock(return_value=mock_member)
    guild.owner_id = 999999999
    return guild


@pytest.fixture
def mock_channel() -> TextChannel:
    """Create a mock discord.TextChannel.

    Returns:
        Mock text channel instance.
    """
    channel = MagicMock()
    channel.id = 777777777
    channel.name = "test-channel"
    channel.mention = "<#777777777>"
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def mock_message(mock_user: User, mock_channel: TextChannel, mock_guild: Guild) -> Message:
    """Create a mock discord.Message.

    Args:
        mock_user: Mock user fixture
        mock_channel: Mock channel fixture
        mock_guild: Mock guild fixture

    Returns:
        Mock message instance.
    """
    message = MagicMock()
    message.id = 888888888
    message.author = mock_user
    message.channel = mock_channel
    message.guild = mock_guild
    message.content = "!test command"
    message.jump_url = f"https://discord.com/channels/{mock_guild.id}/{mock_channel.id}/{message.id}"
    message.created_at = MagicMock()
    message.created_at.strftime = MagicMock(return_value="2024-01-01 12:00:00")
    message.delete = AsyncMock()
    return message


@pytest.fixture
def mock_interaction(mock_user: User, mock_guild: Guild, mock_channel: TextChannel) -> Interaction:
    """Create a mock discord.Interaction.

    Args:
        mock_user: Mock user fixture
        mock_guild: Mock guild fixture
        mock_channel: Mock channel fixture

    Returns:
        Mock interaction instance.
    """
    interaction = MagicMock()
    interaction.user = mock_user
    interaction.guild = mock_guild
    interaction.channel = mock_channel
    interaction.message = None
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    return interaction


@pytest.fixture
def mock_context(
    mock_bot: Bot,
    mock_user: User,
    mock_guild: Guild,
    mock_channel: TextChannel,
    mock_message: Message,
) -> Context:
    """Create a mock discord.ext.commands.Context.

    Args:
        mock_bot: Mock bot fixture
        mock_user: Mock user fixture
        mock_guild: Mock guild fixture
        mock_channel: Mock channel fixture
        mock_message: Mock message fixture

    Returns:
        Mock context instance.
    """
    context = MagicMock()
    context.bot = mock_bot
    context.author = mock_user
    context.guild = mock_guild
    context.channel = mock_channel
    context.message = mock_message
    context.command = MagicMock()
    context.command.name = "test"
    context.interaction = None
    context.send = AsyncMock()
    return context


@pytest.fixture
def mock_api_responses() -> dict[str, dict]:
    """Mock API response data.

    Returns:
        Dictionary of mock API responses.
    """
    guild_id = 555555555
    guild_uuid = str(uuid4())

    return {
        "guild_created": {
            "id": guild_uuid,
            "guild_id": guild_id,
            "guild_name": "Test Guild",
            "prefix": "!",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        },
        "guild_existing": {
            "id": guild_uuid,
            "guild_id": guild_id,
            "guild_name": "Existing Guild",
            "prefix": "?",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        "guild_updated": {
            "id": guild_uuid,
            "guild_id": guild_id,
            "guild_name": "Test Guild",
            "prefix": ">>",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T13:00:00Z",
        },
        "health_check": {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T12:00:00Z",
        },
        "validation_error": {
            "detail": [
                {
                    "type": "string_too_short",
                    "loc": ["body", "guild_name"],
                    "msg": "String should have at least 1 character",
                }
            ]
        },
        "server_error": {"detail": "Internal server error"},
    }


@pytest.fixture
def mock_api_client(respx_mock: respx.MockRouter, mock_api_responses: dict[str, dict]) -> respx.MockRouter:
    """Mock ByteAPIClient HTTP calls using respx.

    Args:
        respx_mock: respx mock router
        mock_api_responses: Mock API response data

    Returns:
        Configured respx mock router.
    """
    base_url = "http://localhost:8000"

    # Health check endpoint
    respx_mock.get(f"{base_url}/health").mock(return_value=Response(200, json=mock_api_responses["health_check"]))

    # Guild endpoints - GET by ID (success)
    respx_mock.get(f"{base_url}/api/guilds/555555555").mock(
        return_value=Response(200, json=mock_api_responses["guild_existing"])
    )

    # Guild endpoints - GET by ID (not found)
    respx_mock.get(f"{base_url}/api/guilds/999999999").mock(return_value=Response(404, json={"detail": "Not found"}))

    # Guild endpoints - POST (create)
    respx_mock.post(f"{base_url}/api/guilds").mock(return_value=Response(201, json=mock_api_responses["guild_created"]))

    return respx_mock
