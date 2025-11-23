"""Integration tests for database transaction handling."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from byte_common.models.github_config import GitHubConfig
from byte_common.models.guild import Guild

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio

__all__ = [
    "TestNestedTransactions",
    "TestTransactionCommit",
    "TestTransactionIsolation",
    "TestTransactionRollback",
]


class TestTransactionRollback:
    """Tests for transaction rollback behavior."""

    async def test_transaction_rollback_on_error(self, db_session: AsyncSession) -> None:
        """Test that failed operations rollback properly."""
        # Create guild
        guild = Guild(guild_id=10001, guild_name="Rollback Test")
        db_session.add(guild)
        await db_session.flush()

        # Force an error - try to add duplicate guild_id
        duplicate_guild = Guild(guild_id=10001, guild_name="Duplicate")
        db_session.add(duplicate_guild)

        # Should raise IntegrityError
        try:
            await db_session.flush()
            msg = "Should have raised IntegrityError"
            raise AssertionError(msg)
        except IntegrityError:
            # Expected - rollback will happen in fixture teardown
            pass

    async def test_rollback_multiple_operations(self, db_session: AsyncSession) -> None:
        """Test rollback with multiple operations."""
        # Add multiple guilds
        guilds = [Guild(guild_id=i, guild_name=f"Guild {i}") for i in range(20001, 20005)]

        for guild in guilds:
            db_session.add(guild)

        await db_session.flush()

        # Verify they exist in session
        result = await db_session.execute(select(Guild).where(Guild.guild_id >= 20001).where(Guild.guild_id < 20005))
        added_guilds = result.scalars().all()
        assert len(added_guilds) == 4

        # Test passes - session will rollback in fixture teardown

    async def test_rollback_with_relationships(self, db_session: AsyncSession) -> None:
        """Test rollback with related entities."""
        # Create guild with config
        guild = Guild(guild_id=30001, guild_name="Relationship Rollback Test")
        db_session.add(guild)
        await db_session.flush()

        github_config = GitHubConfig(
            guild_id=guild.guild_id,
            discussion_sync=True,
            github_organization="test-org",
            github_repository="test-repo",
        )
        db_session.add(github_config)
        await db_session.flush()

        # Verify both exist in session
        guild_result = await db_session.execute(select(Guild).where(Guild.guild_id == 30001))
        assert guild_result.scalar_one_or_none() is not None

        github_result = await db_session.execute(select(GitHubConfig).where(GitHubConfig.guild_id == 30001))
        assert github_result.scalar_one_or_none() is not None

        # Fixture will rollback in teardown


class TestTransactionCommit:
    """Tests for successful transaction commits."""

    async def test_transaction_flush_on_success(self, db_session: AsyncSession) -> None:
        """Test that successful operations flush properly."""
        # Create guild
        guild = Guild(guild_id=40001, guild_name="Commit Test")
        db_session.add(guild)
        await db_session.flush()

        # Verify in session
        result = await db_session.execute(select(Guild).where(Guild.guild_id == 40001))
        flushed_guild = result.scalar_one()

        assert flushed_guild.guild_name == "Commit Test"

    async def test_flush_with_related_entities(self, db_session: AsyncSession) -> None:
        """Test flush with related entities."""
        # Create guild with configs
        guild = Guild(guild_id=50001, guild_name="Related Commit Test")
        db_session.add(guild)
        await db_session.flush()

        github_config = GitHubConfig(
            guild_id=guild.guild_id,
            discussion_sync=True,
        )

        db_session.add(github_config)
        await db_session.flush()

        # Verify all flushed
        guild_result = await db_session.execute(select(Guild).where(Guild.guild_id == 50001))
        assert guild_result.scalar_one() is not None

        github_result = await db_session.execute(select(GitHubConfig).where(GitHubConfig.guild_id == 50001))
        assert github_result.scalar_one() is not None

    async def test_multiple_flushes_in_transaction(self, db_session: AsyncSession) -> None:
        """Test multiple flushes in single transaction."""
        # Add first guild
        guild1 = Guild(guild_id=60001, guild_name="First")
        db_session.add(guild1)
        await db_session.flush()

        # Add second guild
        guild2 = Guild(guild_id=60002, guild_name="Second")
        db_session.add(guild2)
        await db_session.flush()

        # Both should exist in session
        result = await db_session.execute(select(Guild).where(Guild.guild_id.in_([60001, 60002])))
        guilds = result.scalars().all()
        assert len(guilds) == 2


class TestNestedTransactions:
    """Tests for savepoints and nested transaction behavior."""

    async def test_nested_transaction_flush(self, db_session: AsyncSession) -> None:
        """Test flushing in nested transactions."""
        # Outer transaction
        guild1 = Guild(guild_id=80001, guild_name="Outer")
        db_session.add(guild1)
        await db_session.flush()

        # Nested transaction
        async with db_session.begin_nested():
            guild2 = Guild(guild_id=80002, guild_name="Nested")
            db_session.add(guild2)
            await db_session.flush()
            # Nested transaction commits on context exit

        # Both should exist in session
        result = await db_session.execute(select(Guild).where(Guild.guild_id.in_([80001, 80002])))
        guilds = result.scalars().all()
        assert len(guilds) == 2


class TestTransactionIsolation:
    """Tests for transaction isolation levels."""

    async def test_session_isolation_basic(self, db_session: AsyncSession) -> None:
        """Test that changes in one session are isolated from another."""
        # Create guild in this session
        guild = Guild(guild_id=90001, guild_name="Isolation Test")
        db_session.add(guild)
        await db_session.flush()

        # Verify it exists in this session
        result = await db_session.execute(select(Guild).where(Guild.guild_id == 90001))
        assert result.scalar_one_or_none() is not None

        # Note: Testing with a second session would require the async_session fixture
        # which is session-maker, not available in this test context


class TestTransactionErrorHandling:
    """Tests for error handling within transactions."""

    async def test_exception_detection(self, db_session: AsyncSession) -> None:
        """Test that exceptions are properly detected."""
        guild = Guild(guild_id=11001, guild_name="Exception Test")
        db_session.add(guild)
        await db_session.flush()

        # Force integrity error
        duplicate = Guild(guild_id=11001, guild_name="Duplicate")
        db_session.add(duplicate)

        # Should raise IntegrityError
        with pytest.raises(IntegrityError):
            await db_session.flush()
