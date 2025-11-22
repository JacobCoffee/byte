"""Database test fixtures."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from byte_common.models.forum_config import ForumConfig
    from byte_common.models.github_config import GitHubConfig
    from byte_common.models.guild import Guild
    from byte_common.models.user import User

__all__ = [
    "create_sample_guild",
    "create_sample_user",
    "create_sample_github_config",
    "create_sample_forum_config",
]


def create_sample_guild(**kwargs) -> Guild:
    """Create a sample Guild instance for testing.

    Args:
        **kwargs: Override default values.

    Returns:
        Guild instance with test data.
    """
    from byte_common.models.guild import Guild

    defaults = {
        "id": uuid4(),
        "guild_id": 123456789012345678,
        "guild_name": "Test Guild",
        "prefix": "!",
        "help_channel_id": 111111111111111111,
        "showcase_channel_id": 222222222222222222,
        "sync_label": "sync",
        "issue_linking": True,
        "comment_linking": False,
        "pep_linking": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    } | kwargs
    return Guild(**defaults)


def create_sample_user(**kwargs) -> User:
    """Create a sample User instance for testing.

    Args:
        **kwargs: Override default values.

    Returns:
        User instance with test data.
    """
    from byte_common.models.user import User

    defaults = {
        "id": uuid4(),
        "name": "TestUser",
        "avatar_url": "https://example.com/avatar.png",
        "discriminator": "1234",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    } | kwargs
    return User(**defaults)


def create_sample_github_config(guild_id: int | None = None, **kwargs) -> GitHubConfig:
    """Create a sample GitHubConfig instance for testing.

    Args:
        guild_id: Guild ID to associate with (defaults to test guild ID).
        **kwargs: Override default values.

    Returns:
        GitHubConfig instance with test data.
    """
    from byte_common.models.github_config import GitHubConfig

    defaults = {
        "id": uuid4(),
        "guild_id": guild_id or 123456789012345678,
        "discussion_sync": True,
        "github_organization": "test-org",
        "github_repository": "test-repo",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    } | kwargs
    return GitHubConfig(**defaults)


def create_sample_forum_config(guild_id: int | None = None, **kwargs) -> ForumConfig:
    """Create a sample ForumConfig instance for testing.

    Args:
        guild_id: Guild ID to associate with (defaults to test guild ID).
        **kwargs: Override default values.

    Returns:
        ForumConfig instance with test data.
    """
    from byte_common.models.forum_config import ForumConfig

    defaults = {
        "id": uuid4(),
        "guild_id": guild_id or 123456789012345678,
        "help_forum": True,
        "help_forum_category": "Help",
        "help_thread_auto_close": True,
        "help_thread_auto_close_days": 7,
        "help_thread_notify": True,
        "help_thread_notify_roles": "helper,moderator",
        "help_thread_notify_days": 2,
        "showcase_forum": True,
        "showcase_forum_category": "Showcase",
        "showcase_thread_auto_close": False,
        "showcase_thread_auto_close_days": None,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    } | kwargs
    return ForumConfig(**defaults)
