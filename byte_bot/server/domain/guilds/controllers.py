"""Guild controller."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from datetime import timedelta

from litestar import Controller, get, post
from litestar.di import Provide
from litestar.params import Dependency, Parameter
from litestar.security.jwt import JWTAuth, Token
from litestar.connection import ASGIConnection
from litestar.handlers import BaseRouteHandler
from litestar.exceptions import NotAuthorizedException

from byte_bot.server.domain import urls
from byte_bot.server.domain.guilds.dependencies import provides_guilds_service
from byte_bot.server.domain.guilds.schemas import GuildSchema
from byte_bot.server.domain.guilds.services import GuildsService  # noqa: TCH001

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes
    from advanced_alchemy.service import OffsetPagination

__all__ = ("GuildController",)


class GuildController(Controller):
    """Controller for guild-based routes."""

    tags = ["Guilds"]
    dependencies = {"guilds_service": Provide(provides_guilds_service)}

    @get(
        operation_id="Guilds",
        name="guilds:list",
        summary="List Guilds",
        path=urls.GUILD_LIST,
    )
    async def list_guilds(
        self,
        guilds_service: GuildsService,
        filters: list[FilterTypes] = Dependency(skip_validation=True),
    ) -> OffsetPagination[GuildSchema]:
        """List guilds.

        Args:
            guilds_service (GuildsService): Guilds service
            filters (list[FilterTypes]): Filters

        Returns:
            list[Guild]: List of guilds
        """
        results, total = await guilds_service.list_and_count(*filters)
        return guilds_service.to_schema(data=results, total=total, filters=filters, schema_type=GuildSchema)

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
        guild_name: str = Parameter(
            title="Guild Name",
            description="The guild name.",
        ),
    ) -> str:
        """Create a guild.

        Args:
            guilds_service (GuildsService): Guilds service
            guild_id (int): Guild ID
            guild_name (str): Guild name

        Returns:
            Guild: Created guild object
        """
        new_guild = {"guild_id": guild_id, "guild_name": guild_name}
        await guilds_service.create(new_guild)
        return f"Guild {guild_name} created."
