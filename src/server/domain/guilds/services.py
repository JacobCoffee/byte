"""Guild services."""
from __future__ import annotations

from typing import Any

from src.server.domain.db.models import Guild
from src.server.lib import log
from src.server.lib.repository import SQLAlchemyAsyncSlugRepository
from src.server.lib.service import SQLAlchemyAsyncRepositoryService

__all__ = ("GuildsRepository", "GuildsService")


logger = log.get_logger()


class GuildsRepository(SQLAlchemyAsyncSlugRepository[Guild]):
    """Guilds SQLAlchemy Repository."""

    model_type = Guild


class GuildsService(SQLAlchemyAsyncRepositoryService[Guild]):
    """Handles basic operations for a guild."""

    repository_type = GuildsRepository
    match_fields = ["name"]

    async def to_model(self, data: Guild | dict[str, Any], operation: str | None = None) -> Guild:
        """Convert data to a model.

        Args:
            data (Guild | dict[str, Any]): Data to convert to a model
            operation (str | None): Operation to perform on the data

        Returns:
            Project: Converted model
        """
        return await super().to_model(data, operation)
