"""Tests for database layer (ORM, connections, migrations)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from byte_bot.server.domain.db.models import (
    ForumConfig,
    GitHubConfig,
    Guild,
    SOTagsConfig,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

__all__ = (
    "TestDatabaseModels",
    "TestDatabaseRelationships",
)


class TestDatabaseModels:
    """Test suite for database models."""

    @pytest.mark.asyncio
    async def test_all_models_have_tables(self, engine: AsyncEngine) -> None:
        """Test that all models have corresponding database tables.

        Args:
            engine: Database engine
        """

        def check_tables(connection):
            inspector = inspect(connection)
            return inspector.get_table_names()

        async with engine.connect() as conn:
            # Get table names using run_sync to avoid greenlet issues
            table_names = await conn.run_sync(check_tables)

            # Check that core tables exist
            assert "guild" in table_names
            assert "github_config" in table_names
            assert "so_tags_config" in table_names
            assert "allowed_users" in table_names
            assert "user" in table_names
            assert "forum_config" in table_names

    @pytest.mark.asyncio
    async def test_guild_model_fields(self, async_session: AsyncSession) -> None:
        """Test Guild model has expected fields.

        Args:
            async_session: Database session
        """
        guild = Guild(
            guild_id=123456,
            guild_name="Test Guild",
            prefix="!",
            issue_linking=True,
        )
        async_session.add(guild)
        await async_session.commit()

        result = await async_session.execute(select(Guild).where(Guild.guild_id == 123456))
        saved_guild = result.scalar_one()

        # Test fields
        assert hasattr(saved_guild, "id")
        assert hasattr(saved_guild, "guild_id")
        assert hasattr(saved_guild, "guild_name")
        assert hasattr(saved_guild, "prefix")
        assert hasattr(saved_guild, "help_channel_id")
        assert hasattr(saved_guild, "showcase_channel_id")
        assert hasattr(saved_guild, "issue_linking")
        assert hasattr(saved_guild, "comment_linking")
        assert hasattr(saved_guild, "pep_linking")
        assert hasattr(saved_guild, "created_at")
        assert hasattr(saved_guild, "updated_at")


class TestDatabaseRelationships:
    """Test suite for model relationships."""

    @pytest.mark.asyncio
    async def test_guild_github_config_relationship(self, async_session: AsyncSession) -> None:
        """Test Guild <-> GitHubConfig relationship.

        Args:
            async_session: Database session
        """
        # Create guild
        guild = Guild(guild_id=123456, guild_name="Test Guild")
        async_session.add(guild)
        await async_session.flush()

        # Create GitHub config
        github_config = GitHubConfig(
            guild_id=123456,
            discussion_sync=True,
            github_organization="test-org",
            github_repository="test-repo",
        )
        async_session.add(github_config)
        await async_session.commit()

        # Verify relationship
        result = await async_session.execute(select(Guild).where(Guild.guild_id == 123456))
        saved_guild = result.scalar_one()

        # Note: Due to lazy loading being "noload", we need to query the relationship separately
        result = await async_session.execute(select(GitHubConfig).where(GitHubConfig.guild_id == 123456))
        saved_config = result.scalar_one()

        assert saved_config.guild_id == saved_guild.guild_id

    @pytest.mark.asyncio
    async def test_guild_sotags_relationship(self, async_session: AsyncSession) -> None:
        """Test Guild <-> SOTagsConfig relationship.

        Args:
            async_session: Database session
        """
        # Create guild
        guild = Guild(guild_id=123456, guild_name="Test Guild")
        async_session.add(guild)
        await async_session.flush()

        # Create multiple SO tags
        tags = ["python", "litestar", "discord"]
        for tag_name in tags:
            sotag = SOTagsConfig(guild_id=123456, tag_name=tag_name)
            async_session.add(sotag)

        await async_session.commit()

        # Verify relationship
        result = await async_session.execute(select(SOTagsConfig).where(SOTagsConfig.guild_id == 123456))
        saved_tags = result.scalars().all()

        assert len(saved_tags) == 3
        assert all(tag.guild_id == 123456 for tag in saved_tags)

    @pytest.mark.asyncio
    async def test_guild_forum_config_relationship(self, async_session: AsyncSession) -> None:
        """Test Guild <-> ForumConfig relationship.

        Args:
            async_session: Database session
        """
        # Create guild
        guild = Guild(guild_id=123456, guild_name="Test Guild")
        async_session.add(guild)
        await async_session.flush()

        # Create forum config
        forum_config = ForumConfig(
            guild_id=123456,
            help_forum=True,
            help_forum_category="Help",
            showcase_forum=True,
            showcase_forum_category="Showcase",
        )
        async_session.add(forum_config)
        await async_session.commit()

        # Verify relationship
        result = await async_session.execute(select(ForumConfig).where(ForumConfig.guild_id == 123456))
        saved_config = result.scalar_one()

        assert saved_config.guild_id == 123456
        assert saved_config.help_forum is True
        assert saved_config.showcase_forum is True

    @pytest.mark.asyncio
    async def test_cascade_delete_guild(self, async_session: AsyncSession) -> None:
        """Test that deleting a guild cascades to related configs.

        Args:
            async_session: Database session
        """
        # Create guild with related configs
        guild = Guild(guild_id=123456, guild_name="Test Guild")
        async_session.add(guild)
        await async_session.flush()

        # Add related configs
        github_config = GitHubConfig(
            guild_id=123456,
            github_organization="test-org",
            github_repository="test-repo",
        )
        sotag = SOTagsConfig(guild_id=123456, tag_name="python")

        async_session.add_all([github_config, sotag])
        await async_session.commit()

        # Delete the guild
        await async_session.delete(guild)
        await async_session.commit()

        # Verify related configs are deleted
        github_result = await async_session.execute(select(GitHubConfig).where(GitHubConfig.guild_id == 123456))
        assert github_result.scalar_one_or_none() is None

        sotag_result = await async_session.execute(select(SOTagsConfig).where(SOTagsConfig.guild_id == 123456))
        assert sotag_result.scalar_one_or_none() is None
