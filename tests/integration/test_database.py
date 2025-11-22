"""Integration tests for database operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from byte_common.models.forum_config import ForumConfig
from byte_common.models.github_config import GitHubConfig
from byte_common.models.guild import Guild
from byte_common.models.user import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


class TestDatabaseConnection:
    """Tests for database connection and session management."""

    async def test_engine_creation(self, async_engine: AsyncEngine) -> None:
        """Test that async engine is created successfully."""
        assert async_engine is not None
        assert async_engine.url.database == ":memory:"

    async def test_session_creation(self, db_session: AsyncSession) -> None:
        """Test that database session is created successfully."""
        assert db_session is not None
        assert not db_session.is_active or db_session.in_transaction()


class TestGuildCRUD:
    """Tests for Guild CRUD operations."""

    async def test_create_guild(self, db_session: AsyncSession) -> None:
        """Test creating a guild in the database."""
        guild = Guild(
            guild_id=123456789012345678,
            guild_name="Test Guild",
            prefix="!",
        )

        db_session.add(guild)
        await db_session.flush()

        assert guild.id is not None
        assert guild.created_at is not None
        assert guild.updated_at is not None

    async def test_read_guild(self, db_session: AsyncSession, sample_guild: Guild) -> None:
        """Test reading a guild from the database."""
        db_session.add(sample_guild)
        await db_session.flush()
        guild_id = sample_guild.id

        # Read the guild back
        result = await db_session.execute(select(Guild).where(Guild.id == guild_id))
        retrieved_guild = result.scalar_one()

        assert retrieved_guild.id == sample_guild.id
        assert retrieved_guild.guild_id == sample_guild.guild_id
        assert retrieved_guild.guild_name == sample_guild.guild_name

    async def test_update_guild(self, db_session: AsyncSession, sample_guild: Guild) -> None:
        """Test updating a guild in the database."""
        db_session.add(sample_guild)
        await db_session.flush()

        # Update the guild
        sample_guild.guild_name = "Updated Guild Name"
        sample_guild.prefix = "$"
        await db_session.flush()

        # Read back to verify
        result = await db_session.execute(select(Guild).where(Guild.id == sample_guild.id))
        updated_guild = result.scalar_one()

        assert updated_guild.guild_name == "Updated Guild Name"
        assert updated_guild.prefix == "$"

    async def test_delete_guild(self, db_session: AsyncSession, sample_guild: Guild) -> None:
        """Test deleting a guild from the database."""
        db_session.add(sample_guild)
        await db_session.flush()
        guild_id = sample_guild.id

        # Delete the guild
        await db_session.delete(sample_guild)
        await db_session.flush()

        # Verify it's deleted
        result = await db_session.execute(select(Guild).where(Guild.id == guild_id))
        deleted_guild = result.scalar_one_or_none()

        assert deleted_guild is None

    async def test_query_guild_by_guild_id(self, db_session: AsyncSession, sample_guild: Guild) -> None:
        """Test querying guild by Discord guild_id."""
        db_session.add(sample_guild)
        await db_session.flush()

        # Query by guild_id
        result = await db_session.execute(select(Guild).where(Guild.guild_id == sample_guild.guild_id))
        queried_guild = result.scalar_one()

        assert queried_guild.id == sample_guild.id


class TestUserCRUD:
    """Tests for User CRUD operations."""

    async def test_create_user(self, db_session: AsyncSession) -> None:
        """Test creating a user in the database."""
        user = User(
            name="TestUser",
            discriminator="1234",
            avatar_url="https://example.com/avatar.png",
        )

        db_session.add(user)
        await db_session.flush()

        assert user.id is not None
        assert user.created_at is not None

    async def test_read_user(self, db_session: AsyncSession, sample_user: User) -> None:
        """Test reading a user from the database."""
        db_session.add(sample_user)
        await db_session.flush()
        user_id = sample_user.id

        result = await db_session.execute(select(User).where(User.id == user_id))
        retrieved_user = result.scalar_one()

        assert retrieved_user.name == sample_user.name
        assert retrieved_user.discriminator == sample_user.discriminator


class TestRelationships:
    """Tests for model relationships."""

    async def test_guild_github_config_relationship(
        self,
        db_session: AsyncSession,
        sample_guild: Guild,
    ) -> None:
        """Test Guild to GitHubConfig one-to-one relationship."""
        db_session.add(sample_guild)
        await db_session.flush()

        # Create GitHub config
        github_config = GitHubConfig(
            guild_id=sample_guild.guild_id,
            discussion_sync=True,
            github_organization="test-org",
            github_repository="test-repo",
        )
        db_session.add(github_config)
        await db_session.flush()

        # Query GitHub config and verify relationship
        result = await db_session.execute(
            select(GitHubConfig).where(GitHubConfig.guild_id == sample_guild.guild_id)
        )
        retrieved_config = result.scalar_one()

        assert retrieved_config.guild_id == sample_guild.guild_id
        assert retrieved_config.github_organization == "test-org"

    async def test_guild_forum_config_relationship(
        self,
        db_session: AsyncSession,
        sample_guild: Guild,
    ) -> None:
        """Test Guild to ForumConfig one-to-one relationship."""
        db_session.add(sample_guild)
        await db_session.flush()

        # Create Forum config
        forum_config = ForumConfig(
            guild_id=sample_guild.guild_id,
            help_forum=True,
            showcase_forum=True,
        )
        db_session.add(forum_config)
        await db_session.flush()

        # Query Forum config and verify relationship
        result = await db_session.execute(select(ForumConfig).where(ForumConfig.guild_id == sample_guild.guild_id))
        retrieved_config = result.scalar_one()

        assert retrieved_config.guild_id == sample_guild.guild_id
        assert retrieved_config.help_forum is True

    async def test_cascade_delete_github_config(
        self,
        db_session: AsyncSession,
        sample_guild: Guild,
    ) -> None:
        """Test cascade delete of GitHubConfig when Guild is deleted."""
        db_session.add(sample_guild)
        await db_session.flush()

        github_config = GitHubConfig(
            guild_id=sample_guild.guild_id,
            discussion_sync=True,
        )
        db_session.add(github_config)
        await db_session.flush()
        config_id = github_config.id

        # Delete guild
        await db_session.delete(sample_guild)
        await db_session.flush()

        # Verify GitHub config was cascade deleted
        result = await db_session.execute(select(GitHubConfig).where(GitHubConfig.id == config_id))
        deleted_config = result.scalar_one_or_none()

        assert deleted_config is None

    async def test_cascade_delete_forum_config(
        self,
        db_session: AsyncSession,
        sample_guild: Guild,
    ) -> None:
        """Test cascade delete of ForumConfig when Guild is deleted."""
        db_session.add(sample_guild)
        await db_session.flush()

        forum_config = ForumConfig(
            guild_id=sample_guild.guild_id,
            help_forum=True,
        )
        db_session.add(forum_config)
        await db_session.flush()
        config_id = forum_config.id

        # Delete guild
        await db_session.delete(sample_guild)
        await db_session.flush()

        # Verify Forum config was cascade deleted
        result = await db_session.execute(select(ForumConfig).where(ForumConfig.id == config_id))
        deleted_config = result.scalar_one_or_none()

        assert deleted_config is None


class TestTransactions:
    """Tests for transaction handling."""

    async def test_transaction_rollback(self, async_session: async_sessionmaker[AsyncSession]) -> None:
        """Test that session rollback works correctly.

        Uses a fresh session to test rollback behavior independently.
        """
        async with async_session() as session:
            guild = Guild(
                guild_id=123456789012345678,
                guild_name="Test Guild",
            )

            session.add(guild)
            await session.flush()
            guild_id = guild.id

            # Rollback the session (don't commit)
            await session.rollback()

        # In a new session, verify guild was not persisted
        async with async_session() as session:
            result = await session.execute(select(Guild).where(Guild.id == guild_id))
            rolled_back_guild = result.scalar_one_or_none()

            # Guild should not exist since we rolled back
            assert rolled_back_guild is None

    async def test_multiple_operations_in_transaction(self, db_session: AsyncSession) -> None:
        """Test multiple operations in a single transaction."""
        # Create guild
        guild = Guild(
            guild_id=123456789012345678,
            guild_name="Test Guild",
        )
        db_session.add(guild)
        await db_session.flush()

        # Create related configs
        github_config = GitHubConfig(
            guild_id=guild.guild_id,
            discussion_sync=True,
        )
        forum_config = ForumConfig(
            guild_id=guild.guild_id,
            help_forum=True,
        )
        db_session.add(github_config)
        db_session.add(forum_config)
        await db_session.flush()

        # Verify all were created
        result = await db_session.execute(select(Guild).where(Guild.guild_id == guild.guild_id))
        assert result.scalar_one() is not None

        result = await db_session.execute(select(GitHubConfig).where(GitHubConfig.guild_id == guild.guild_id))
        assert result.scalar_one() is not None

        result = await db_session.execute(select(ForumConfig).where(ForumConfig.guild_id == guild.guild_id))
        assert result.scalar_one() is not None


class TestQueryOperations:
    """Tests for various query operations."""

    async def test_filter_guilds_by_prefix(self, db_session: AsyncSession) -> None:
        """Test filtering guilds by prefix."""
        guild1 = Guild(guild_id=111111111111111111, guild_name="Guild 1", prefix="!")
        guild2 = Guild(guild_id=222222222222222222, guild_name="Guild 2", prefix="$")
        guild3 = Guild(guild_id=333333333333333333, guild_name="Guild 3", prefix="!")

        db_session.add_all([guild1, guild2, guild3])
        await db_session.flush()

        # Query guilds with prefix '!'
        result = await db_session.execute(select(Guild).where(Guild.prefix == "!"))
        guilds_with_bang = result.scalars().all()

        assert len(guilds_with_bang) == 2
        assert all(g.prefix == "!" for g in guilds_with_bang)

    async def test_count_guilds(self, db_session: AsyncSession) -> None:
        """Test counting guilds."""
        guild1 = Guild(guild_id=111111111111111111, guild_name="Guild 1")
        guild2 = Guild(guild_id=222222222222222222, guild_name="Guild 2")

        db_session.add_all([guild1, guild2])
        await db_session.flush()

        # Count guilds
        from sqlalchemy import func

        result = await db_session.execute(select(func.count()).select_from(Guild))
        count = result.scalar()

        assert count == 2
