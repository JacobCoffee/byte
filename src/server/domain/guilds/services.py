"""Guild services."""
from __future__ import annotations

from typing import Any

from server.domain.db.models import GuildConfig
from server.lib import log
from server.lib.repository import SQLAlchemyAsyncSlugRepository
from server.lib.service import SQLAlchemyAsyncRepositoryService

__all__ = ("GuildsRepository", "GuildsService")


logger = log.get_logger()


class GuildsRepository(SQLAlchemyAsyncSlugRepository[GuildConfig]):
    """Guilds SQLAlchemy Repository."""

    model_type = GuildConfig


class GuildsService(SQLAlchemyAsyncRepositoryService[GuildConfig]):
    """Handles basic operations for a guild."""

    repository_type = GuildsRepository
    match_fields = ["name"]

    async def to_model(self, data: GuildConfig | dict[str, Any], operation: str | None = None) -> GuildConfig:
        """Convert data to a model.

        Args:
            data (GuildConfig | dict[str, Any]): Data to convert to a model
            operation (str | None): Operation to perform on the data

        Returns:
            Project: Converted model
        """
        if isinstance(data, dict) and "slug" not in data and operation == "create":
            data["slug"] = await self.repository.get_available_slug(data["name"])  # type: ignore[union-attr]
        return await super().to_model(data, operation)
