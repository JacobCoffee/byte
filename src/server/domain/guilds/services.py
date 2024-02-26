"""Guild services."""
from __future__ import annotations

from typing import Any, TypeVar

from server.domain.db.models import AllowedUsersConfig, GitHubConfig, Guild, SOTagsConfig
from server.lib import log
from server.lib.repository import SQLAlchemyAsyncRepository, SQLAlchemyAsyncSlugRepository
from server.lib.service import SQLAlchemyAsyncRepositoryService

__all__ = (
    "AllowedUsersConfigRepository",
    "AllowedUsersConfigService",
    "GuildRepository",
    "GuildService",
    "GitHubConfigRepository",
    "GitHubConfigService",
    "SOTagsConfigRepository",
    "SOTagsConfigService",
)

T = TypeVar("T")

logger = log.get_logger()


class GuildRepository(SQLAlchemyAsyncSlugRepository[Guild]):
    """Guild Config SQLAlchemy Repository."""

    model_type = Guild


class GuildService(SQLAlchemyAsyncRepositoryService[Guild]):
    """Handles basic operations for a guild."""

    repository_type = GuildRepository
    match_fields = ["name"]

    async def to_model(self, data: Guild | dict[str, Any], operation: str | None = None) -> Guild:
        """Convert data of Guild to a model of Guild.

        Args:
            data (Guild | dict[str, Any]): Data to convert to a model
            operation (str | None): Operation to perform on the data

        Returns:
            Guild: Converted model
        """
        if isinstance(data, dict) and "slug" not in data and operation == "create":
            data["slug"] = await self.repository.get_available_slug(data["name"])  # type: ignore[attr-defined]
        return await super().to_model(data, operation)


class GitHubConfigRepository(SQLAlchemyAsyncRepository[GitHubConfig]):
    """GitHubConfig SQLAlchemy Repository."""

    model_type = GitHubConfig


class GitHubConfigService(SQLAlchemyAsyncRepositoryService[GitHubConfig]):
    """Handles basic operations for the guilds' GitHub config."""

    repository_type = GitHubConfigRepository


class SOTagsConfigRepository(SQLAlchemyAsyncRepository[SOTagsConfig]):
    """SOTagsConfig SQLAlchemy Repository."""

    model_type = SOTagsConfig


class SOTagsConfigService(SQLAlchemyAsyncRepositoryService[SOTagsConfig]):
    """Handles basic operations for the guilds' StackOverflow tags config."""

    repository_type = SOTagsConfigRepository


class AllowedUsersConfigRepository(SQLAlchemyAsyncRepository[AllowedUsersConfig]):
    """AllowedUsersConfig SQLAlchemy Repository."""

    model_type = AllowedUsersConfig


class AllowedUsersConfigService(SQLAlchemyAsyncRepositoryService[AllowedUsersConfig]):
    """Handles basic operations for the guilds' Allowed Users config."""

    repository_type = AllowedUsersConfigRepository
