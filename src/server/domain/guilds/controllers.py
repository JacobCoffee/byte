"""User Account Controllers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, get
from litestar.di import Provide

from src.server.domain import urls
from src.server.domain.db.models import GuildConfig  # noqa: TCH001
from src.server.domain.guilds.dependencies import provides_guild_config_service
from src.server.domain.guilds.services import GuildConfigService  # noqa: TCH001

if TYPE_CHECKING:
    from litestar.pagination import OffsetPagination

__all__ = ["GuildsController"]


class GuildsController(Controller):
    """Routes for guilds."""

    tags = ["Guilds"]
    dependencies = {"guilds_service": Provide(provides_guild_config_service)}

    @get(
        operation_id="ListTeams",
        name="teams:list",
        summary="List Teams",
        path=urls.GUILDS_LIST,
    )
    async def list_guilds(
        self,
        guilds_service: GuildConfigService,
        # filters: list[FilterTypes] = Dependency(skip_validation=True),
    ) -> OffsetPagination[GuildConfig]:
        """List guilds.

        .. todo:: Add guards and return only what the user can access.
            Re-enable filters after resolving ``ImproperlyConfiguredException``.
        """
        results, total = await guilds_service.list_and_count()
        return guilds_service.to_dto(results, total)
