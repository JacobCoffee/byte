"""Tests for guild services and repositories."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from byte_api.domain.guilds.services import (
    AllowedUsersConfigRepository,
    AllowedUsersConfigService,
    ForumConfigRepository,
    ForumConfigService,
    GitHubConfigRepository,
    GitHubConfigService,
    GuildsRepository,
    GuildsService,
    SOTagsConfigRepository,
    SOTagsConfigService,
)
from byte_common.models import AllowedUsersConfig, ForumConfig, GitHubConfig, Guild, SOTagsConfig, User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = [
    "test_allowed_users_config_get_by_guild_id_not_found",
    "test_allowed_users_config_get_by_guild_id_success",
    "test_allowed_users_config_repository_create",
    "test_allowed_users_config_service_operations",
    "test_forum_config_get_by_guild_id_not_found",
    "test_forum_config_get_by_guild_id_success",
    "test_forum_config_repository_type",
    "test_forum_config_service_bug_fix_verification",
    "test_forum_config_service_operations",
    "test_github_config_get_by_guild_id_not_found",
    "test_github_config_get_by_guild_id_success",
    "test_github_config_repository_create",
    "test_github_config_service_match_fields",
    "test_guilds_repository_create",
    "test_guilds_repository_delete",
    "test_guilds_repository_get",
    "test_guilds_repository_list",
    "test_guilds_repository_update",
    "test_guilds_service_create",
    "test_guilds_service_match_fields",
    "test_sotags_config_get_by_guild_id_not_found",
    "test_sotags_config_get_by_guild_id_success",
    "test_sotags_config_repository_create",
    "test_sotags_config_service_operations",
]


# --- GuildsRepository Tests ---


@pytest.mark.asyncio
@pytest.mark.unit
async def test_guilds_repository_create(db_session: AsyncSession) -> None:
    """Test creating a guild via repository."""
    repo = GuildsRepository(session=db_session)

    guild_data = {
        "guild_id": 123456789012345678,
        "guild_name": "Test Guild",
        "prefix": "!",
    }

    guild = await repo.add(Guild(**guild_data))
    await db_session.flush()

    assert guild.guild_id == guild_data["guild_id"]
    assert guild.guild_name == guild_data["guild_name"]
    assert guild.prefix == guild_data["prefix"]
    assert guild.id is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_guilds_repository_get(db_session: AsyncSession, sample_guild: Guild) -> None:
    """Test retrieving a guild by ID."""
    repo = GuildsRepository(session=db_session)

    # Add guild
    created_guild = await repo.add(sample_guild)
    await db_session.flush()  # Flush to DB but don't commit (fixture handles that)

    # Retrieve guild
    retrieved_guild = await repo.get(created_guild.id)

    assert retrieved_guild.id == created_guild.id
    assert retrieved_guild.guild_id == sample_guild.guild_id
    assert retrieved_guild.guild_name == sample_guild.guild_name


@pytest.mark.asyncio
@pytest.mark.unit
async def test_guilds_repository_list(db_session: AsyncSession) -> None:
    """Test listing all guilds."""
    repo = GuildsRepository(session=db_session)

    # Create multiple guilds
    guild1 = Guild(guild_id=111111111111111111, guild_name="Guild 1")
    guild2 = Guild(guild_id=222222222222222222, guild_name="Guild 2")

    await repo.add(guild1)
    await repo.add(guild2)
    await db_session.flush()

    # List guilds
    guilds = await repo.list()

    assert len(guilds) == 2
    guild_names = {g.guild_name for g in guilds}
    assert "Guild 1" in guild_names
    assert "Guild 2" in guild_names


@pytest.mark.asyncio
@pytest.mark.unit
async def test_guilds_repository_update(db_session: AsyncSession, sample_guild: Guild) -> None:
    """Test updating a guild."""
    repo = GuildsRepository(session=db_session)

    # Create guild
    created_guild = await repo.add(sample_guild)
    await db_session.flush()

    # Update guild
    updated_guild = await repo.update(
        Guild(
            id=created_guild.id,
            guild_id=created_guild.guild_id,
            guild_name="Updated Guild Name",
            prefix="?",
        )
    )
    await db_session.flush()

    assert updated_guild.guild_name == "Updated Guild Name"
    assert updated_guild.prefix == "?"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_guilds_repository_delete(db_session: AsyncSession, sample_guild: Guild) -> None:
    """Test deleting a guild."""
    repo = GuildsRepository(session=db_session)

    # Create guild
    created_guild = await repo.add(sample_guild)
    await db_session.flush()

    # Delete guild
    deleted_guild = await repo.delete(created_guild.id)
    await db_session.flush()

    assert deleted_guild.id == created_guild.id

    # Verify deletion
    result = await db_session.execute(select(Guild).where(Guild.id == created_guild.id))
    assert result.scalar_one_or_none() is None


# --- GuildsService Tests ---


@pytest.mark.asyncio
@pytest.mark.unit
async def test_guilds_service_create(db_session: AsyncSession) -> None:
    """Test creating a guild via service."""
    service = GuildsService(session=db_session)

    guild_dict = {
        "guild_id": 987654321098765432,
        "guild_name": "Service Test Guild",
        "prefix": "$",
    }

    guild = await service.create(guild_dict)
    assert guild.guild_id == guild_dict["guild_id"]
    assert guild.guild_name == guild_dict["guild_name"]
    assert guild.prefix == guild_dict["prefix"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_guilds_service_match_fields(db_session: AsyncSession) -> None:
    """Test that GuildsService has correct match_fields configuration."""
    service = GuildsService(session=db_session)

    assert service.match_fields == ["guild_id"]


# --- GitHubConfigRepository Tests ---


@pytest.mark.asyncio
@pytest.mark.unit
async def test_github_config_repository_create(db_session: AsyncSession, sample_guild: Guild) -> None:
    """Test creating a GitHub config via repository."""
    # Create guild first
    guild_repo = GuildsRepository(session=db_session)
    await guild_repo.add(sample_guild)
    await db_session.flush()

    # Create GitHub config
    repo = GitHubConfigRepository(session=db_session)
    config_data = {
        "guild_id": sample_guild.guild_id,
        "github_organization": "test-org",
        "github_repository": "test-repo",
        "discussion_sync": True,
    }

    config = await repo.add(GitHubConfig(**config_data))
    await db_session.flush()

    assert config.guild_id == sample_guild.guild_id
    assert config.github_organization == "test-org"
    assert config.github_repository == "test-repo"
    assert config.discussion_sync is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_github_config_service_match_fields(db_session: AsyncSession) -> None:
    """Test that GitHubConfigService has correct match_fields."""
    service = GitHubConfigService(session=db_session)

    assert service.match_fields == ["guild_id"]


# --- SOTagsConfigRepository Tests ---


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sotags_config_repository_create(db_session: AsyncSession, sample_guild: Guild) -> None:
    """Test creating SO tags config via repository."""
    # Create guild first
    guild_repo = GuildsRepository(session=db_session)
    await guild_repo.add(sample_guild)
    await db_session.flush()

    # Create SO tags config
    repo = SOTagsConfigRepository(session=db_session)
    tag_data = {
        "guild_id": sample_guild.guild_id,
        "tag_name": "python",
    }

    tag = await repo.add(SOTagsConfig(**tag_data))
    await db_session.flush()

    assert tag.guild_id == sample_guild.guild_id
    assert tag.tag_name == "python"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sotags_config_service_operations(db_session: AsyncSession, sample_guild: Guild) -> None:
    """Test SOTagsConfigService CRUD operations."""
    # Create guild first
    guild_repo = GuildsRepository(session=db_session)
    await guild_repo.add(sample_guild)
    await db_session.flush()

    service = SOTagsConfigService(session=db_session)

    # Create multiple tags
    tag1 = await service.create({"guild_id": sample_guild.guild_id, "tag_name": "python"})
    tag2 = await service.create({"guild_id": sample_guild.guild_id, "tag_name": "javascript"})

    assert tag1.tag_name == "python"
    assert tag2.tag_name == "javascript"
    assert service.match_fields == ["guild_id"]


# --- AllowedUsersConfigRepository Tests ---


@pytest.mark.asyncio
@pytest.mark.unit
async def test_allowed_users_config_repository_create(
    db_session: AsyncSession,
    sample_guild: Guild,
    sample_user: User,
) -> None:
    """Test creating allowed users config via repository."""

    # Create guild and user first
    guild_repo = GuildsRepository(session=db_session)
    await guild_repo.add(sample_guild)
    await db_session.flush()

    # Add user to DB
    await db_session.merge(sample_user)
    await db_session.flush()

    # Create allowed user config
    repo = AllowedUsersConfigRepository(session=db_session)
    user_config_data = {
        "guild_id": sample_guild.guild_id,
        "user_id": sample_user.id,
    }

    user_config = await repo.add(AllowedUsersConfig(**user_config_data))
    await db_session.flush()

    assert user_config.guild_id == sample_guild.guild_id
    assert user_config.user_id == sample_user.id


@pytest.mark.asyncio
@pytest.mark.unit
async def test_allowed_users_config_service_operations(
    db_session: AsyncSession,
    sample_guild: Guild,
    sample_user: User,
) -> None:
    """Test AllowedUsersConfigService operations."""
    # Create guild and user first
    guild_repo = GuildsRepository(session=db_session)
    await guild_repo.add(sample_guild)
    await db_session.flush()

    await db_session.merge(sample_user)
    await db_session.flush()

    service = AllowedUsersConfigService(session=db_session)

    # Create user config
    user_config = await service.create(
        {
            "guild_id": sample_guild.guild_id,
            "user_id": sample_user.id,
        }
    )

    assert user_config.user_id == sample_user.id
    assert service.match_fields == ["guild_id"]


# --- ForumConfigRepository Tests (BUG FIX VERIFICATION) ---


@pytest.mark.asyncio
@pytest.mark.unit
async def test_forum_config_repository_type(db_session: AsyncSession) -> None:
    """CRITICAL: Verify ForumConfigService uses ForumConfigRepository, not AllowedUsersConfigRepository.

    This test verifies the bug fix where ForumConfigService was incorrectly
    using AllowedUsersConfigRepository instead of ForumConfigRepository.
    """
    service = ForumConfigService(session=db_session)

    # Verify the repository_type is correct
    assert service.repository_type == ForumConfigRepository
    assert service.repository_type != AllowedUsersConfigRepository

    # Verify it can instantiate the correct repository
    repo = service.repository_type(session=db_session)
    assert isinstance(repo, ForumConfigRepository)
    assert repo.model_type == ForumConfig


@pytest.mark.asyncio
@pytest.mark.unit
async def test_forum_config_service_operations(db_session: AsyncSession, sample_guild: Guild) -> None:
    """Test ForumConfigService can perform CRUD operations with correct repository."""
    # Create guild first
    guild_repo = GuildsRepository(session=db_session)
    await guild_repo.add(sample_guild)
    await db_session.flush()

    service = ForumConfigService(session=db_session)

    # Create forum config using the service
    forum_config = await service.create(
        {
            "guild_id": sample_guild.guild_id,
            "help_forum": True,
            "help_forum_category": "Help",
            "help_thread_auto_close": True,
            "help_thread_auto_close_days": 7,
            "showcase_forum": False,
        }
    )

    # Verify the config was created with correct data
    assert forum_config.guild_id == sample_guild.guild_id
    assert forum_config.help_forum is True
    assert forum_config.help_forum_category == "Help"
    assert forum_config.help_thread_auto_close is True
    assert forum_config.help_thread_auto_close_days == 7
    assert forum_config.showcase_forum is False

    # Verify match_fields
    assert service.match_fields == ["guild_id"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_forum_config_service_bug_fix_verification(db_session: AsyncSession, sample_guild: Guild) -> None:
    """CRITICAL BUG FIX VERIFICATION: Ensure ForumConfig operations actually work.

    This test verifies that the ForumConfigService bug fix is effective by
    performing real database operations that would have failed with the wrong repository.
    """
    # Create guild
    guild_repo = GuildsRepository(session=db_session)
    await guild_repo.add(sample_guild)
    await db_session.flush()

    service = ForumConfigService(session=db_session)

    # Create forum config with list[int] for help_thread_notify_roles
    created_config = await service.create(
        {
            "guild_id": sample_guild.guild_id,
            "help_forum": True,
            "help_forum_category": "Support",
            "help_thread_auto_close": False,
            "help_thread_notify": True,
            "help_thread_notify_roles": [123456789, 987654321],  # list[int] not string
            "help_thread_notify_days": 3,
            "showcase_forum": True,
            "showcase_forum_category": "Projects",
            "showcase_thread_auto_close": False,
        }
    )

    # Retrieve it back using get() to verify persistence
    retrieved_config = await service.get(created_config.id)

    # Verify all fields match
    assert retrieved_config.guild_id == sample_guild.guild_id
    assert retrieved_config.help_forum is True
    assert retrieved_config.help_forum_category == "Support"
    assert retrieved_config.help_thread_auto_close is False
    assert retrieved_config.help_thread_notify is True
    assert retrieved_config.help_thread_notify_roles == [123456789, 987654321]  # list[int] comparison
    assert retrieved_config.help_thread_notify_days == 3
    assert retrieved_config.showcase_forum is True
    assert retrieved_config.showcase_forum_category == "Projects"
    assert retrieved_config.showcase_thread_auto_close is False

    # Update the config
    updated_config = await service.update(
        {"help_thread_auto_close": True, "help_thread_auto_close_days": 14},
        item_id=created_config.id,
    )

    assert updated_config.help_thread_auto_close is True
    assert updated_config.help_thread_auto_close_days == 14

    # List configs for this guild
    configs, count = await service.list_and_count()
    assert count >= 1
    assert any(c.id == created_config.id for c in configs)


# --- get_by_guild_id Helper Method Tests ---


@pytest.mark.asyncio
@pytest.mark.unit
async def test_github_config_get_by_guild_id_success(db_session: AsyncSession, sample_guild: Guild) -> None:
    """Test GitHubConfigService.get_by_guild_id returns config for valid guild."""
    guild_repo = GuildsRepository(session=db_session)
    await guild_repo.add(sample_guild)
    await db_session.flush()

    service = GitHubConfigService(session=db_session)
    created_config = await service.create(
        {
            "guild_id": sample_guild.guild_id,
            "github_organization": "test-org",
            "github_repository": "test-repo",
            "discussion_sync": True,
        }
    )

    result = await service.get_by_guild_id(sample_guild.guild_id)

    assert result.id == created_config.id
    assert result.guild_id == sample_guild.guild_id
    assert result.github_organization == "test-org"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_github_config_get_by_guild_id_not_found(db_session: AsyncSession) -> None:
    """Test GitHubConfigService.get_by_guild_id raises NotFoundError for missing config."""
    from advanced_alchemy.exceptions import NotFoundError

    service = GitHubConfigService(session=db_session)

    with pytest.raises(NotFoundError):
        await service.get_by_guild_id(999999999)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sotags_config_get_by_guild_id_success(db_session: AsyncSession, sample_guild: Guild) -> None:
    """Test SOTagsConfigService.get_by_guild_id returns config for valid guild."""
    guild_repo = GuildsRepository(session=db_session)
    await guild_repo.add(sample_guild)
    await db_session.flush()

    service = SOTagsConfigService(session=db_session)
    created_config = await service.create(
        {
            "guild_id": sample_guild.guild_id,
            "tag_name": "python",
        }
    )

    result = await service.get_by_guild_id(sample_guild.guild_id)

    assert result.id == created_config.id
    assert result.guild_id == sample_guild.guild_id
    assert result.tag_name == "python"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_sotags_config_get_by_guild_id_not_found(db_session: AsyncSession) -> None:
    """Test SOTagsConfigService.get_by_guild_id raises NotFoundError for missing config."""
    from advanced_alchemy.exceptions import NotFoundError

    service = SOTagsConfigService(session=db_session)

    with pytest.raises(NotFoundError):
        await service.get_by_guild_id(999999999)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_allowed_users_config_get_by_guild_id_success(
    db_session: AsyncSession,
    sample_guild: Guild,
    sample_user: User,
) -> None:
    """Test AllowedUsersConfigService.get_by_guild_id returns config for valid guild."""
    guild_repo = GuildsRepository(session=db_session)
    await guild_repo.add(sample_guild)
    await db_session.flush()

    await db_session.merge(sample_user)
    await db_session.flush()

    service = AllowedUsersConfigService(session=db_session)
    created_config = await service.create(
        {
            "guild_id": sample_guild.guild_id,
            "user_id": sample_user.id,
        }
    )

    result = await service.get_by_guild_id(sample_guild.guild_id)

    assert result.id == created_config.id
    assert result.guild_id == sample_guild.guild_id


@pytest.mark.asyncio
@pytest.mark.unit
async def test_allowed_users_config_get_by_guild_id_not_found(db_session: AsyncSession) -> None:
    """Test AllowedUsersConfigService.get_by_guild_id raises NotFoundError for missing config."""
    from advanced_alchemy.exceptions import NotFoundError

    service = AllowedUsersConfigService(session=db_session)

    with pytest.raises(NotFoundError):
        await service.get_by_guild_id(999999999)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_forum_config_get_by_guild_id_success(db_session: AsyncSession, sample_guild: Guild) -> None:
    """Test ForumConfigService.get_by_guild_id returns config for valid guild."""
    guild_repo = GuildsRepository(session=db_session)
    await guild_repo.add(sample_guild)
    await db_session.flush()

    service = ForumConfigService(session=db_session)
    created_config = await service.create(
        {
            "guild_id": sample_guild.guild_id,
            "help_forum": True,
            "help_forum_category": "Help",
            "help_thread_auto_close": False,
            "showcase_forum": False,
        }
    )

    result = await service.get_by_guild_id(sample_guild.guild_id)

    assert result.id == created_config.id
    assert result.guild_id == sample_guild.guild_id
    assert result.help_forum is True
    assert result.help_forum_category == "Help"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_forum_config_get_by_guild_id_not_found(db_session: AsyncSession) -> None:
    """Test ForumConfigService.get_by_guild_id raises NotFoundError for missing config."""
    from advanced_alchemy.exceptions import NotFoundError

    service = ForumConfigService(session=db_session)

    with pytest.raises(NotFoundError):
        await service.get_by_guild_id(999999999)
