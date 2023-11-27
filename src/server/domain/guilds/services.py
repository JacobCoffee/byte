"""Guild services."""
from __future__ import annotations

from typing import Any, TypeVar

from src.server.domain.db.models import GuildAllowedUsersConfig, GuildConfig, GuildGitHubConfig, GuildSOTagsConfig
from src.server.lib import log
from src.server.lib.repository import SQLAlchemyAsyncRepository, SQLAlchemyAsyncSlugRepository
from src.server.lib.service import SQLAlchemyAsyncRepositoryService

__all__ = (
    "GuildAllowedUsersConfigRepository",
    "GuildAllowedUsersConfigService",
    "GuildConfigRepository",
    "GuildConfigService",
    "GuildGitHubConfigRepository",
    "GuildGitHubConfigService",
    "GuildSOTagsConfigRepository",
    "GuildSOTagsConfigService",
)

T = TypeVar("T")

logger = log.get_logger()


class GuildConfigRepository(SQLAlchemyAsyncSlugRepository[GuildConfig]):
    """Guild Config SQLAlchemy Repository."""

    model_type = GuildConfig


class GuildConfigService(SQLAlchemyAsyncRepositoryService[GuildConfig]):
    """Handles basic operations for a guild."""

    repository_type = GuildConfigRepository
    match_fields = ["name"]

    async def to_model(self, data: GuildConfig | dict[str, Any], operation: str | None = None) -> GuildConfig:
        """Convert data of GuildConfig to a model of GuildConfig.

        Args:
            data (GuildConfig | dict[str, Any]): Data to convert to a model
            operation (str | None): Operation to perform on the data

        Returns:
            GuildConfig: Converted model
        """
        if isinstance(data, dict) and "slug" not in data and operation == "create":
            data["slug"] = await self.repository.get_available_slug(data["name"])  # type: ignore[attr-defined]
        return await super().to_model(data, operation)


class GuildGitHubConfigRepository(SQLAlchemyAsyncRepository[GuildGitHubConfig]):
    """GuildGitHubConfig SQLAlchemy Repository."""

    model_type = GuildGitHubConfig


class GuildGitHubConfigService(SQLAlchemyAsyncRepositoryService[GuildGitHubConfig]):
    """Handles basic operations for the guilds' GitHub config."""

    repository_type = GuildGitHubConfigRepository


class GuildSOTagsConfigRepository(SQLAlchemyAsyncRepository[GuildSOTagsConfig]):
    """GuildSOTagsConfig SQLAlchemy Repository."""

    model_type = GuildSOTagsConfig


class GuildSOTagsConfigService(SQLAlchemyAsyncRepositoryService[GuildSOTagsConfig]):
    """Handles basic operations for the guilds' StackOverflow tags config."""

    repository_type = GuildSOTagsConfigRepository


class GuildAllowedUsersConfigRepository(SQLAlchemyAsyncRepository[GuildAllowedUsersConfig]):
    """GuildAllowedUsersConfig SQLAlchemy Repository."""

    model_type = GuildAllowedUsersConfig


class GuildAllowedUsersConfigService(SQLAlchemyAsyncRepositoryService[GuildAllowedUsersConfig]):
    """Handles basic operations for the guilds' Allowed Users config."""

    repository_type = GuildAllowedUsersConfigRepository
