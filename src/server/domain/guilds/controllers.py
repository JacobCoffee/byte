"""Guild controller."""
from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, get, post
from litestar.di import Provide
from litestar.params import Parameter

from server.domain import urls
from server.domain.guilds.dependencies import provides_guilds_service
from server.domain.guilds.schemas import GuildSchema  # noqa: TCH001
from server.domain.guilds.services import GuildsService  # noqa: TCH001

__all__ = ("GuildController",)


if TYPE_CHECKING:
    from litestar.pagination import OffsetPagination


class GuildController(Controller):
    """Controller for guild-based routes."""

    tags = ["Guilds"]
    dependencies = {"guilds_service": Provide(provides_guilds_service)}

    @get(
        operation_id="Guilds",
        name="guilds:list",
        summary="List Guilds",
        path=urls.GUILD_CREATE,
    )
    async def list_guilds(
        self,
        guilds_service: GuildsService,
        # filters: list[FilterTypes] = Dependency(skip_validation=True),
    ) -> OffsetPagination[GuildSchema]:
        """List guilds.

        Args:
            guilds_service (GuildsService): Guilds service
            filters (list[FilterTypes]): Filters

        Returns:
            list[Guild]: List of guilds
        """
        # results, total = await guilds_service.list_and_count(*filters)
        # return guilds_service.to_schema(GuildSchema, results, total, *filters)

    @post(
        operation_id="CreateGuild",
        name="guilds:create",
        summary="Create a new guild.",
        path=urls.GUILD_CREATE,
    )
    async def create_guild(
        self,
        guilds_service: GuildsService,
        guild_id: int = Parameter(
            title="Guild ID",
            description="The guild ID.",
        ),
    ) -> str:
        """Create a guild.

        Args:
            guilds_service (GuildsService): Guilds service
            guild_id (int): Guild ID

        Returns:
            str: The guild ID
        """
        return await guilds_service.create(guild_id)
