"""Guild controller."""

from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, get, patch, post
from litestar.di import Provide
from litestar.params import Dependency, Parameter

from byte_bot.server.domain.db.models import Guild
from byte_bot.server.domain.guilds import urls
from byte_bot.server.domain.guilds.dependencies import provides_guilds_service
from byte_bot.server.domain.guilds.schemas import GuildSchema, UpdateableGuildSetting
from byte_bot.server.domain.guilds.services import GuildsService  # noqa: TCH001

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes
    from advanced_alchemy.service import OffsetPagination

__all__ = ("GuildsController",)


class GuildsController(Controller):
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

    @patch(
        operation_id="UpdateGuild",
        name="guilds:update",
        summary="Update a guild.",
        path=urls.GUILD_UPDATE,
    )
    async def update_guild(
        self,
        guilds_service: GuildsService,
        guild_id: int = Parameter(
            title="Guild ID",
            description="The guild ID.",
        ),
        setting: UpdateableGuildSetting = Parameter(
            title="Setting",
            description="The setting to update.",
        ),
        value: str | int = Parameter(
            title="Value",
            description="The new value for the setting.",
        ),
    ) -> GuildSchema | OffsetPagination[GuildSchema]:
        """Update a guild by ID.

        Args:
            guilds_service (GuildsService): Guilds service
            guild_id (Guild.guild_id): Guild ID
            setting (UpdateableGuildSetting): Setting to update
            value (str | int): New value for the setting

        Returns:
            Guild: Updated guild object
        """
        _guild = guilds_service.get(guild_id, id_attribute="guild_id")
        # todo: this is a placeholder, update to grab whichever setting is being update, and update the corresponding
        #       tables value
        await guilds_service.update(_guild, setting, {"some-config-thing": value})
        return guilds_service.to_schema(GuildSchema, _guild)

    @get(
        operation_id="GuildDetail",
        name="guilds:detail",
        summary="Get guild details.",
        path=urls.GUILD_DETAIL,
    )
    async def get_guild(
        self,
        guilds_service: GuildsService,
        guild_id: int = Parameter(
            title="Guild ID",
            description="The guild ID.",
        ),
    ) -> GuildSchema:
        """Get a guild by ID.

        Args:
            guilds_service (GuildsService): Guilds service
            guild_id (int): Guild ID

        Returns:
            Guild: Guild object
        """
        result = await guilds_service.get(guild_id, id_attribute="guild_id")
        return guilds_service.to_schema(GuildSchema, result)
