"""Guild services."""

from __future__ import annotations

from typing import TYPE_CHECKING

from advanced_alchemy.repository import SQLAlchemyAsyncSlugRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from byte_bot.server.domain.db.models import Guild
from byte_bot.server.lib import log

__all__ = ("GuildsRepository", "GuildsService")

logger = log.get_logger()


class GuildsRepository(SQLAlchemyAsyncSlugRepository[Guild]):
    """Guilds SQLAlchemy Repository."""

    model_type = Guild


class GuildsService(SQLAlchemyAsyncRepositoryService[Guild]):
    """Handles basic operations for a guild."""

    repository_type = GuildsRepository
    match_fields = ["guild_id"]

    async def to_model(self, data: ModelDictT[Guild], operation: str | None = None) -> Guild:
        """Convert data to a model.

        Args:
            data (ModelDictT[Guild]): Data to convert to a model
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

    async def to_model(self, data: ModelDictT[GitHubConfig], operation: str | None = None) -> GitHubConfig:
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

    async def to_model(self, data: ModelDictT[SOTagsConfig], operation: str | None = None) -> SOTagsConfig:
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

    async def to_model(self, data: ModelDictT[AllowedUsersConfig], operation: str | None = None) -> AllowedUsersConfig:
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

    async def to_model(self, data: ModelDictT[ForumConfig], operation: str | None = None) -> ForumConfig:
        """Convert data to a model.

        Args:
            data (ForumConfig | dict[str, Any]): Data to convert to a model
            operation (str | None): Operation to perform on the data

        Returns:
            Project: Converted model
        """
        return await super().to_model(data, operation)
