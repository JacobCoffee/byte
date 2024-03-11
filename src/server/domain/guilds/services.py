"""Guild services."""

from __future__ import annotations

from typing import Any

from server.domain.db.models import AllowedUsersConfig, ForumConfig, GitHubConfig, Guild, SOTagsConfig
from server.lib import log
from server.lib.repository import SQLAlchemyAsyncRepository, SQLAlchemyAsyncSlugRepository
from server.lib.service import SQLAlchemyAsyncRepositoryService

__all__ = (
    "AllowedUsersConfigRepository",
    "AllowedUsersConfigService",
    "ForumConfigRepository",
    "ForumConfigService",
    "GitHubConfigRepository",
    "GitHubConfigService",
    "GuildsRepository",
    "GuildsService",
    "SOTagsConfigRepository",
    "SOTagsConfigService",
)

logger = log.get_logger()


class GuildsRepository(SQLAlchemyAsyncSlugRepository[Guild]):
    """Guilds SQLAlchemy Repository."""

    model_type = Guild


class GuildsService(SQLAlchemyAsyncRepositoryService[Guild]):
    """Handles basic operations for a guild."""

    repository_type = GuildsRepository
    match_fields = ["guild_id"]

    async def to_model(self, data: Guild | dict[str, Any], operation: str | None = None) -> Guild:
        """Convert data to a model.

        Args:
            data (Guild | dict[str, Any]): Data to convert to a model
            operation (str | None): Operation to perform on the data

        Returns:
            Project: Converted model
        """
        return await super().to_model(data, operation)


class GitHubConfigRepository(SQLAlchemyAsyncRepository[GitHubConfig]):
    """GitHubConfig SQLAlchemy Repository."""

    model_type = GitHubConfig


class GitHubConfigService(SQLAlchemyAsyncRepositoryService[GitHubConfig]):
    """Handles basic operations for the guilds' GitHub config."""

    repository_type = GitHubConfigRepository
    match_fields = ["guild_id"]

    async def to_model(self, data: GitHubConfig | dict[str, Any], operation: str | None = None) -> GitHubConfig:
        """Convert data to a model.

        Args:
            data (GitHubConfig | dict[str, Any]): Data to convert to a model
            operation (str | None): Operation to perform on the data

        Returns:
            Project: Converted model
        """
        return await super().to_model(data, operation)


class SOTagsConfigRepository(SQLAlchemyAsyncRepository[SOTagsConfig]):
    """SOTagsConfig SQLAlchemy Repository."""

    model_type = SOTagsConfig


class SOTagsConfigService(SQLAlchemyAsyncRepositoryService[SOTagsConfig]):
    """Handles basic operations for the guilds' StackOverflow tags config."""

    repository_type = SOTagsConfigRepository
    match_fields = ["guild_id"]

    async def to_model(self, data: SOTagsConfig | dict[str, Any], operation: str | None = None) -> SOTagsConfig:
        """Convert data to a model.

        Args:
            data (SOTagsConfig | dict[str, Any]): Data to convert to a model
            operation (str | None): Operation to perform on the data

        Returns:
            Project: Converted model
        """
        return await super().to_model(data, operation)


class AllowedUsersConfigRepository(SQLAlchemyAsyncRepository[AllowedUsersConfig]):
    """AllowedUsersConfig SQLAlchemy Repository."""

    model_type = AllowedUsersConfig


class AllowedUsersConfigService(SQLAlchemyAsyncRepositoryService[AllowedUsersConfig]):
    """Handles basic operations for the guilds' Allowed Users config."""

    repository_type = AllowedUsersConfigRepository
    match_fields = ["guild_id"]

    async def to_model(
        self, data: AllowedUsersConfig | dict[str, Any], operation: str | None = None
    ) -> AllowedUsersConfig:
        """Convert data to a model.

        Args:
            data (AllowedUsersConfig | dict[str, Any]): Data to convert to a model
            operation (str | None): Operation to perform on the data

        Returns:
            Project: Converted model
        """
        return await super().to_model(data, operation)


class ForumConfigRepository(SQLAlchemyAsyncRepository[ForumConfig]):
    """ForumConfig SQLAlchemy Repository."""

    model_type = ForumConfig


class ForumConfigService(SQLAlchemyAsyncRepositoryService[ForumConfig]):
    """Handles basic operations for the guilds' Forum config."""

    repository_type = AllowedUsersConfigRepository
    match_fields = ["guild_id"]

    async def to_model(self, data: ForumConfig | dict[str, Any], operation: str | None = None) -> ForumConfig:
        """Convert data to a model.

        Args:
            data (ForumConfig | dict[str, Any]): Data to convert to a model
            operation (str | None): Operation to perform on the data

        Returns:
            Project: Converted model
        """
        return await super().to_model(data, operation)
