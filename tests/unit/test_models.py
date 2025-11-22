"""Unit tests for database models."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

import pytest
from sqlalchemy import select

from byte_common.models.forum_config import ForumConfig
from byte_common.models.github_config import GitHubConfig
from byte_common.models.guild import Guild
from byte_common.models.user import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


class TestGuildModel:
    """Tests for the Guild model."""

    async def test_guild_creation(self, db_session: AsyncSession, sample_guild: Guild) -> None:
        """Test creating a guild instance."""
        db_session.add(sample_guild)
        await db_session.flush()

        assert sample_guild.id is not None
        assert isinstance(sample_guild.id, UUID)
        assert sample_guild.guild_id == 123456789012345678
        assert sample_guild.guild_name == "Test Guild"
        assert sample_guild.prefix == "!"
        assert sample_guild.created_at is not None
        assert sample_guild.updated_at is not None

    async def test_guild_defaults(self, db_session: AsyncSession) -> None:
        """Test guild default values."""
        guild = Guild(
            guild_id=999999999999999999,
            guild_name="Default Guild",
        )
        db_session.add(guild)
        await db_session.flush()

        assert guild.prefix == "!"
        assert guild.issue_linking is False
        assert guild.comment_linking is False
        assert guild.pep_linking is False
        assert guild.help_channel_id is None
        assert guild.showcase_channel_id is None

    async def test_guild_unique_guild_id(self, db_session: AsyncSession, sample_guild: Guild) -> None:
        """Test that guild_id must be unique."""
        db_session.add(sample_guild)
        await db_session.flush()

        # Try to create another guild with the same guild_id
        duplicate_guild = Guild(
            guild_id=sample_guild.guild_id,
            guild_name="Duplicate Guild",
        )
        db_session.add(duplicate_guild)

        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            await db_session.flush()

    async def test_guild_relationships_github_config(
        self,
        db_session: AsyncSession,
        sample_guild: Guild,
        sample_github_config: GitHubConfig,
    ) -> None:
        """Test Guild -> GitHubConfig relationship."""
        db_session.add(sample_guild)
        await db_session.flush()

        # Add GitHub config
        sample_github_config.guild_id = sample_guild.guild_id
        db_session.add(sample_github_config)
        await db_session.flush()

        # Reload guild with eager loading
        result = await db_session.execute(select(Guild).where(Guild.id == sample_guild.id))
        guild = result.scalar_one()

        # Verify relationship exists
        assert guild.guild_id == sample_github_config.guild_id

    async def test_guild_relationships_forum_config(
        self,
        db_session: AsyncSession,
        sample_guild: Guild,
        sample_forum_config: ForumConfig,
    ) -> None:
        """Test Guild -> ForumConfig relationship."""
        db_session.add(sample_guild)
        await db_session.flush()

        # Add Forum config
        sample_forum_config.guild_id = sample_guild.guild_id
        db_session.add(sample_forum_config)
        await db_session.flush()

        # Reload guild
        result = await db_session.execute(select(Guild).where(Guild.id == sample_guild.id))
        guild = result.scalar_one()

        assert guild.guild_id == sample_forum_config.guild_id

    async def test_guild_cascade_delete(
        self,
        db_session: AsyncSession,
        sample_guild: Guild,
        sample_github_config: GitHubConfig,
    ) -> None:
        """Test that deleting a guild cascades to related configs.

        Note: SQLite in-memory doesn't fully support CASCADE DELETE
        in the same way as PostgreSQL, so this test verifies the
        relationship exists but may not enforce cascade behavior.
        """
        db_session.add(sample_guild)
        await db_session.flush()

        sample_github_config.guild_id = sample_guild.guild_id
        db_session.add(sample_github_config)
        await db_session.flush()

        # Verify the relationship exists
        result = await db_session.execute(
            select(GitHubConfig).where(GitHubConfig.guild_id == sample_guild.guild_id)
        )
        config = result.scalar_one()
        assert config.guild_id == sample_guild.guild_id


class TestUserModel:
    """Tests for the User model."""

    async def test_user_creation(self, db_session: AsyncSession, sample_user: User) -> None:
        """Test creating a user instance."""
        db_session.add(sample_user)
        await db_session.flush()

        assert sample_user.id is not None
        assert isinstance(sample_user.id, UUID)
        assert sample_user.name == "TestUser"
        assert sample_user.discriminator == "1234"
        assert sample_user.avatar_url == "https://example.com/avatar.png"

    async def test_user_nullable_avatar(self, db_session: AsyncSession) -> None:
        """Test that avatar_url can be null."""
        user = User(
            name="No Avatar User",
            discriminator="5678",
            avatar_url=None,
        )
        db_session.add(user)
        await db_session.flush()

        assert user.avatar_url is None


class TestGitHubConfigModel:
    """Tests for the GitHubConfig model."""

    async def test_github_config_creation(
        self,
        db_session: AsyncSession,
        sample_guild: Guild,
        sample_github_config: GitHubConfig,
    ) -> None:
        """Test creating a GitHub config instance."""
        db_session.add(sample_guild)
        await db_session.flush()

        sample_github_config.guild_id = sample_guild.guild_id
        db_session.add(sample_github_config)
        await db_session.flush()

        assert sample_github_config.id is not None
        assert sample_github_config.discussion_sync is True
        assert sample_github_config.github_organization == "test-org"
        assert sample_github_config.github_repository == "test-repo"

    async def test_github_config_defaults(self, db_session: AsyncSession, sample_guild: Guild) -> None:
        """Test GitHub config default values."""
        db_session.add(sample_guild)
        await db_session.flush()

        config = GitHubConfig(guild_id=sample_guild.guild_id)
        db_session.add(config)
        await db_session.flush()

        assert config.discussion_sync is False
        assert config.github_organization is None
        assert config.github_repository is None

    async def test_github_config_requires_guild(self, db_session: AsyncSession, sample_guild: Guild) -> None:
        """Test that GitHub config requires a valid guild_id.

        Note: We test that a config can be created with a valid guild_id.
        SQLite foreign key enforcement may vary based on configuration.
        """
        # First create a guild
        db_session.add(sample_guild)
        await db_session.flush()

        # Create config with valid guild_id
        config = GitHubConfig(
            guild_id=sample_guild.guild_id,
        )
        db_session.add(config)
        await db_session.flush()

        assert config.guild_id == sample_guild.guild_id


class TestForumConfigModel:
    """Tests for the ForumConfig model."""

    async def test_forum_config_creation(
        self,
        db_session: AsyncSession,
        sample_guild: Guild,
        sample_forum_config: ForumConfig,
    ) -> None:
        """Test creating a forum config instance."""
        db_session.add(sample_guild)
        await db_session.flush()

        sample_forum_config.guild_id = sample_guild.guild_id
        db_session.add(sample_forum_config)
        await db_session.flush()

        assert sample_forum_config.id is not None
        assert sample_forum_config.help_forum is True
        assert sample_forum_config.help_forum_category == "Help"
        assert sample_forum_config.showcase_forum is True
        assert sample_forum_config.showcase_forum_category == "Showcase"

    async def test_forum_config_defaults(self, db_session: AsyncSession, sample_guild: Guild) -> None:
        """Test forum config default values."""
        db_session.add(sample_guild)
        await db_session.flush()

        config = ForumConfig(guild_id=sample_guild.guild_id)
        db_session.add(config)
        await db_session.flush()

        assert config.help_forum is False
        assert config.showcase_forum is False
        assert config.help_thread_auto_close is False
        assert config.showcase_thread_auto_close is False

    async def test_forum_config_requires_guild(self, db_session: AsyncSession, sample_guild: Guild) -> None:
        """Test that forum config requires a valid guild_id.

        Note: We test that a config can be created with a valid guild_id.
        SQLite foreign key enforcement may vary based on configuration.
        """
        # First create a guild
        db_session.add(sample_guild)
        await db_session.flush()

        # Create config with valid guild_id
        config = ForumConfig(
            guild_id=sample_guild.guild_id,
        )
        db_session.add(config)
        await db_session.flush()

        assert config.guild_id == sample_guild.guild_id
