"""Guild services."""

from __future__ import annotations

from typing import TYPE_CHECKING

from advanced_alchemy.repository import SQLAlchemyAsyncSlugRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from byte_bot.server.domain.db.models import Guild
from byte_bot.server.lib import log

if TYPE_CHECKING:
    from advanced_alchemy.service.typing import ModelDictT

__all__ = ("GuildsRepository", "GuildsService")


logger = log.get_logger()


class GuildsRepository(SQLAlchemyAsyncSlugRepository[Guild]):
    """Guilds SQLAlchemy Repository."""

    model_type = Guild


class GuildsService(SQLAlchemyAsyncRepositoryService[Guild]):
    """Handles basic operations for a guild."""

    repository_type = GuildsRepository
    match_fields = ["name"]

    async def to_model(self, data: ModelDictT[Guild], operation: str | None = None) -> Guild:
        """Convert data to a model.

        Args:
            data (ModelDictT[Guild]): Data to convert to a model
            operation (str | None): Operation to perform on the data

        Returns:
            Project: Converted model
        """
        return await super().to_model(data, operation)
