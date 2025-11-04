"""Shared test fixtures and configuration for the Byte test suite.

This module provides fixtures for both the web app (Litestar) and Discord bot components.
"""

from __future__ import annotations

import os

# Set up test environment variables BEFORE any imports
os.environ["ENVIRONMENT"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DISCORD_TOKEN"] = "test-token"
os.environ["DISCORD_DEV_GUILD_ID"] = "123456789"
os.environ["DISCORD_DEV_USER_ID"] = "987654321"

from collections.abc import AsyncGenerator, Generator
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from litestar import Litestar
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

if TYPE_CHECKING:
    import discord
    from discord.ext.commands import Bot

__all__ = (
    "app",
    "async_session",
    "client",
    "engine",
    "mock_bot",
    "mock_discord_guild",
    "mock_discord_member",
    "mock_discord_message",
    "sample_allowed_user",
    "sample_forum_config",
    "sample_github_config",
    "sample_guild",
    "sample_sotags_config",
    "sample_user",
)


# =================
# Database Fixtures
# =================


@pytest.fixture(scope="function")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create a test database engine.

    Uses an in-memory SQLite database for testing.

    Yields:
        AsyncEngine: SQLAlchemy async engine
    """
    # Import here to avoid circular imports
    from advanced_alchemy.base import UUIDAuditBase

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(UUIDAuditBase.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session.

    Args:
        engine: Test database engine

    Yields:
        AsyncSession: SQLAlchemy async session
    """
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
        await session.rollback()


# =================
# Litestar App Fixtures
# =================


@pytest.fixture(scope="function")
async def app(engine: AsyncEngine) -> AsyncGenerator[Litestar, None]:
    """Create a test Litestar application.

    Args:
        engine: Test database engine

    Yields:
        Litestar: Test application instance
    """
    # Import here to avoid circular imports
    from advanced_alchemy.extensions.litestar import AsyncSessionConfig, SQLAlchemyAsyncConfig
    from advanced_alchemy.extensions.litestar.plugins import SQLAlchemyInitPlugin

    from byte_bot.app import create_app

    session_config = AsyncSessionConfig(expire_on_commit=False)
    sqlalchemy_config = SQLAlchemyAsyncConfig(
        engine_instance=engine,
        session_config=session_config,
    )

    # Create app with test database
    app = create_app()

    # Replace the database plugin with our test database
    for i, plugin in enumerate(app.plugins):
        if isinstance(plugin, SQLAlchemyInitPlugin):
            app.plugins[i] = SQLAlchemyInitPlugin(config=sqlalchemy_config)
            break

    yield app


@pytest.fixture(scope="function")
async def client(app: Litestar) -> AsyncGenerator[AsyncTestClient, None]:
    """Create a test HTTP client.

    Args:
        app: Test Litestar application

    Yields:
        AsyncTestClient: Litestar test client
    """
    async with AsyncTestClient(app=app, base_url="http://testserver") as client:
        yield client


# =================
# Model Fixtures
# =================


@pytest.fixture
def sample_guild() -> dict[str, Any]:
    """Create sample guild data.

    Returns:
        dict: Guild data
    """
    return {
        "guild_id": 123456789,
        "guild_name": "Test Guild",
        "prefix": "!",
        "help_channel_id": 111111111,
        "showcase_channel_id": 222222222,
        "issue_linking": True,
        "comment_linking": True,
        "pep_linking": False,
    }


@pytest.fixture
def sample_github_config(sample_guild: dict[str, Any]) -> dict[str, Any]:
    """Create sample GitHub config data.

    Args:
        sample_guild: Sample guild data

    Returns:
        dict: GitHub config data
    """
    return {
        "guild_id": sample_guild["guild_id"],
        "discussion_sync": True,
        "github_organization": "test-org",
        "github_repository": "test-repo",
    }


@pytest.fixture
def sample_sotags_config(sample_guild: dict[str, Any]) -> dict[str, Any]:
    """Create sample Stack Overflow tags config data.

    Args:
        sample_guild: Sample guild data

    Returns:
        dict: SO tags config data
    """
    return {
        "guild_id": sample_guild["guild_id"],
        "tag_name": "python",
    }


@pytest.fixture
def sample_user() -> dict[str, Any]:
    """Create sample user data.

    Returns:
        dict: User data
    """
    return {
        "name": "TestUser",
        "avatar_url": "https://example.com/avatar.png",
        "discriminator": "1234",
    }


@pytest.fixture
def sample_allowed_user(sample_guild: dict[str, Any], sample_user: dict[str, Any]) -> dict[str, Any]:
    """Create sample allowed user config data.

    Args:
        sample_guild: Sample guild data
        sample_user: Sample user data

    Returns:
        dict: Allowed user config data
    """
    return {
        "guild_id": sample_guild["guild_id"],
        "user_id": uuid4(),
    }


@pytest.fixture
def sample_forum_config(sample_guild: dict[str, Any]) -> dict[str, Any]:
    """Create sample forum config data.

    Args:
        sample_guild: Sample guild data

    Returns:
        dict: Forum config data
    """
    return {
        "guild_id": sample_guild["guild_id"],
        "help_forum": True,
        "help_forum_category": "Help",
        "help_thread_auto_close": True,
        "help_thread_auto_close_days": 7,
        "help_thread_notify": True,
        "help_thread_notify_roles": "Support",
        "help_thread_notify_days": 2,
        "showcase_forum": True,
        "showcase_forum_category": "Showcase",
        "showcase_thread_auto_close": False,
        "showcase_thread_auto_close_days": None,
    }


# =================
# Discord Bot Fixtures
# =================


@pytest.fixture
def mock_discord_guild() -> MagicMock:
    """Create a mock Discord guild.

    Returns:
        MagicMock: Mock Discord guild
    """
    guild = MagicMock(spec=["id", "name", "members", "channels", "get_channel"])
    guild.id = 123456789
    guild.name = "Test Guild"
    guild.members = []
    guild.channels = []
    guild.get_channel = MagicMock(return_value=None)
    return guild


@pytest.fixture
def mock_discord_member(mock_discord_guild: MagicMock) -> MagicMock:
    """Create a mock Discord member.

    Args:
        mock_discord_guild: Mock Discord guild

    Returns:
        MagicMock: Mock Discord member
    """
    member = MagicMock(spec=["id", "name", "discriminator", "bot", "guild", "mention", "avatar", "send"])
    member.id = 987654321
    member.name = "TestUser"
    member.discriminator = "1234"
    member.bot = False
    member.guild = mock_discord_guild
    member.mention = "<@987654321>"
    member.avatar = None
    member.send = AsyncMock()
    return member


@pytest.fixture
def mock_discord_message(mock_discord_member: MagicMock, mock_discord_guild: MagicMock) -> MagicMock:
    """Create a mock Discord message.

    Args:
        mock_discord_member: Mock Discord member
        mock_discord_guild: Mock Discord guild

    Returns:
        MagicMock: Mock Discord message
    """
    message = MagicMock(
        spec=["id", "content", "author", "guild", "channel", "created_at", "jump_url", "add_reaction"]
    )
    message.id = 111111111
    message.content = "!test command"
    message.author = mock_discord_member
    message.guild = mock_discord_guild
    message.channel = MagicMock(spec=["id", "name", "mention", "send"])
    message.channel.id = 222222222
    message.channel.name = "general"
    message.channel.mention = "<#222222222>"
    message.channel.send = AsyncMock()
    message.created_at = MagicMock()
    message.jump_url = "https://discord.com/channels/123456789/222222222/111111111"
    message.add_reaction = AsyncMock()
    return message


@pytest.fixture
def mock_bot() -> AsyncMock:
    """Create a mock Discord bot.

    Returns:
        AsyncMock: Mock Discord bot
    """
    bot = AsyncMock(spec=["user", "guilds", "get_guild", "process_commands", "load_extension", "tree"])
    bot.user = MagicMock(spec=["id", "name", "discriminator"])
    bot.user.id = 999999999
    bot.user.name = "ByteBot"
    bot.user.discriminator = "0000"
    bot.guilds = []
    bot.get_guild = MagicMock(return_value=None)
    bot.process_commands = AsyncMock()
    bot.load_extension = AsyncMock()
    bot.tree = MagicMock(spec=["sync", "copy_global_to"])
    bot.tree.sync = AsyncMock()
    bot.tree.copy_global_to = MagicMock()
    return bot
