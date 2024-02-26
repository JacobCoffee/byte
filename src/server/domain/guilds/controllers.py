"""Guilds Controllers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, get
from litestar.di import Provide

from server.domain.db.models import Guild  # noqa: TCH001
from server.domain.guilds import urls as guild_urls
from server.domain.guilds.dependencies import provides_guild_config_service
from server.domain.guilds.services import GuildService  # noqa: TCH001

if TYPE_CHECKING:
    from litestar.pagination import OffsetPagination

__all__ = ["GuildsController"]


class GuildsController(Controller):
    """Routes for guilds."""

    tags = ["Guilds"]
    dependencies = {"guilds_service": Provide(provides_guild_config_service)}

    @get(
        operation_id="ListGuilds",
        name="guilds:list",
        summary="List all guilds",
        path=guild_urls.GUILD_LIST,
    )
    async def list_guilds(
        self,
        guilds_service: GuildService,
        # filters: list[FilterTypes] = Dependency(skip_validation=True),
    ) -> OffsetPagination[Guild]:
        """List guilds.

        .. todo:: Add guards and return only what the user can access.
            Re-enable filters after resolving ``ImproperlyConfiguredException``.
        """
        results, total = await guilds_service.list_and_count()
        return guilds_service.to_dto(results, total)
