"""Shared pytest fixtures for all tests."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

import pytest
from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from tests.fixtures.db_fixtures import (
    create_sample_forum_config,
    create_sample_github_config,
    create_sample_guild,
    create_sample_user,
)

if TYPE_CHECKING:
    from byte_common.models.forum_config import ForumConfig
    from byte_common.models.github_config import GitHubConfig
    from byte_common.models.guild import Guild
    from byte_common.models.user import User

__all__ = [
    "async_engine",
    "async_session",
    "db_session",
    "sample_forum_config",
    "sample_github_config",
    "sample_guild",
    "sample_user",
]


@pytest.fixture(scope="function")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create an async SQLite engine for testing.

    Uses in-memory SQLite database that's created fresh for each test.
    """
    from sqlalchemy import event

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )

    # Enable foreign key constraints in SQLite
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(UUIDAuditBase.metadata.create_all)

    try:
        yield engine
    finally:
        # Drop all tables and close connections
        async with engine.begin() as conn:
            await conn.run_sync(UUIDAuditBase.metadata.drop_all)
        await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(async_engine: AsyncEngine) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    """Create an async session factory for testing."""
    session_factory = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield session_factory


@pytest.fixture(scope="function")
async def db_session(async_session: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing.

    Automatically rolls back after each test.
    """
    async with async_session() as session:
        async with session.begin():
            yield session
            # Rollback happens automatically when context exits


@pytest.fixture
def sample_guild() -> Guild:
    """Create a sample Guild instance for testing."""
    return create_sample_guild()


@pytest.fixture
def sample_user() -> User:
    """Create a sample User instance for testing."""
    return create_sample_user()


@pytest.fixture
def sample_github_config(sample_guild: Guild) -> GitHubConfig:
    """Create a sample GitHubConfig instance for testing."""
    return create_sample_github_config(guild_id=sample_guild.guild_id)


@pytest.fixture
def sample_forum_config(sample_guild: Guild) -> ForumConfig:
    """Create a sample ForumConfig instance for testing."""
    return create_sample_forum_config(guild_id=sample_guild.guild_id)
