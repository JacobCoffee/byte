"""Guild controller."""

from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, get, patch, post
from litestar.di import Provide
from litestar.params import Dependency, Parameter

from byte_bot.server.domain.guilds import urls
from byte_bot.server.domain.guilds.dependencies import (
    provides_allowed_users_config_service,
    provides_forum_config_service,
    provides_github_config_service,
    provides_guilds_service,
    provides_sotags_config_service,
)
from byte_bot.server.domain.guilds.schemas import (
    AllowedUsersConfigSchema,
    ForumConfigSchema,
    GitHubConfigSchema,
    GuildSchema,
    SOTagsConfigSchema,
    UpdateableGuildSettingEnum,
)
from byte_bot.server.domain.guilds.services import (
    AllowedUsersConfigService,  # noqa: TC001
    ForumConfigService,  # noqa: TC001
    GitHubConfigService,  # noqa: TC001
    GuildsService,  # noqa: TC001
    SOTagsConfigService,  # noqa: TC001
)

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes
    from advanced_alchemy.service import OffsetPagination

__all__ = ("GuildsController",)


class GuildsController(Controller):
    """Controller for guild-based routes."""

    tags = ["Guilds"]
    dependencies = {
        "guilds_service": Provide(provides_guilds_service),
        "github_service": Provide(provides_github_config_service),
        "sotags_service": Provide(provides_sotags_config_service),
        "allowed_users_service": Provide(provides_allowed_users_config_service),
        "forum_service": Provide(provides_forum_config_service),
    }

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
        setting: UpdateableGuildSettingEnum = Parameter(  # type: ignore[valid-type]
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
            setting (str): Setting to update
            value (str | int): New value for the setting

        Returns:
            Guild: Updated guild object
        """
        result = await guilds_service.get(guild_id, id_attribute="guild_id")
        # todo: this is a placeholder, update to grab whichever setting is being update, and update the corresponding
        #       tables value based on the setting parameter
        await guilds_service.update({setting.value: value}, item_id=guild_id)
        return guilds_service.to_schema(schema_type=GuildSchema, data=result)

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
        return guilds_service.to_schema(schema_type=GuildSchema, data=result)

    @get(
        operation_id="GitHubDetail",
        name="guilds:github-config",
        summary="Get GitHub config for a guild.",
        path=urls.GUILD_GITHUB_DETAIL,
    )
    async def get_guild_github_config(
        self,
        github_service: GitHubConfigService,
        guild_id: int = Parameter(
            title="Guild ID",
            description="The guild ID.",
        ),
    ) -> GitHubConfigSchema | OffsetPagination[GitHubConfigSchema]:
        """Get a guild's GitHub config by ID.

        TODO(#88): a helper method that we can use outside of routes would be nice.

        Args:
            github_service (GitHubConfigService): GitHub config service
            guild_id (int): Guild ID

        Returns:
            GitHubConfig: GitHub config object
        """
        result = await github_service.get(guild_id, id_attribute="guild_id")
        return github_service.to_schema(schema_type=GitHubConfigSchema, data=result)

    @get(
        operation_id="SOTagsDetail",
        name="guilds:sotags-config",
        summary="Get StackOverflow tags config for a guild.",
        path=urls.GUILD_SOTAGS_DETAIL,
    )
    async def get_guild_sotags_config(
        self,
        sotags_service: SOTagsConfigService,
        guild_id: int = Parameter(
            title="Guild ID",
            description="The guild ID.",
        ),
    ) -> SOTagsConfigSchema | OffsetPagination[SOTagsConfigSchema]:
        """Get a guild's StackOverflow tags config by ID.

        Args:
            sotags_service (SOTagsConfigService): StackOverflow tags config service
            guild_id (int): Guild ID

        Returns:
            SOTagsConfig: StackOverflow tags config object
        """
        result = await sotags_service.get(guild_id, id_attribute="guild_id")
        return sotags_service.to_schema(schema_type=SOTagsConfigSchema, data=result)

    @get(
        operation_id="AllowedUsersDetail",
        name="guilds:allowed-users-config",
        summary="Get allowed users config for a guild.",
        path=urls.GUILD_ALLOWED_USERS_DETAIL,
    )
    async def get_guild_allowed_users_config(
        self,
        allowed_users_service: AllowedUsersConfigService,
        guild_id: int = Parameter(
            title="Guild ID",
            description="The guild ID.",
        ),
    ) -> AllowedUsersConfigSchema | OffsetPagination[AllowedUsersConfigSchema]:
        """Get a guild's allowed users config by ID.

        Args:
            allowed_users_service (AllowedUsersConfigService): Allowed users config service
            guild_id (int): Guild ID

        Returns:
            AllowedUsersConfig: Allowed users config object
        """
        result = await allowed_users_service.get(guild_id, id_attribute="guild_id")
        return allowed_users_service.to_schema(schema_type=AllowedUsersConfigSchema, data=result)

    @get(
        operation_id="ForumDetail",
        name="guilds:forum-config",
        summary="Get forum config for a guild.",
        path=urls.GUILD_FORUM_DETAIL,
    )
    async def get_guild_forum_config(
        self,
        forum_service: ForumConfigService,
        guild_id: int = Parameter(
            title="Guild ID",
            description="The guild ID.",
        ),
    ) -> ForumConfigSchema | OffsetPagination[ForumConfigSchema]:
        """Get a guild's forum config by ID.

        Args:
            forum_service (ForumConfigService): Forum config service
            guild_id (int): Guild ID

        Returns:
            ForumConfig: Forum config object
        """
        result = await forum_service.get(guild_id, id_attribute="guild_id")
        return forum_service.to_schema(schema_type=ForumConfigSchema, data=result)

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
        return guilds_service.to_schema(schema_type=GuildSchema, data=result)

    @get(
        operation_id="GitHubDetail",
        name="guilds:github-config",
        summary="Get GitHub config for a guild.",
        path=urls.GUILD_GITHUB_DETAIL,
    )
    async def get_guild_github_config(
        self,
        github_service: GitHubConfigService,
        guild_id: int = Parameter(
            title="Guild ID",
            description="The guild ID.",
        ),
    ) -> GitHubConfigSchema | OffsetPagination[GitHubConfigSchema]:
        """Get a guild's GitHub config by ID.

        TODO(#88): a helper method that we can use outside of routes would be nice.

        Args:
            github_service (GitHubConfigService): GitHub config service
            guild_id (int): Guild ID

        Returns:
            GitHubConfig: GitHub config object
        """
        result = await github_service.get(guild_id, id_attribute="guild_id")
        return github_service.to_schema(schema_type=GitHubConfigSchema, data=result)

    @get(
        operation_id="SOTagsDetail",
        name="guilds:sotags-config",
        summary="Get StackOverflow tags config for a guild.",
        path=urls.GUILD_SOTAGS_DETAIL,
    )
    async def get_guild_sotags_config(
        self,
        sotags_service: SOTagsConfigService,
        guild_id: int = Parameter(
            title="Guild ID",
            description="The guild ID.",
        ),
    ) -> SOTagsConfigSchema | OffsetPagination[SOTagsConfigSchema]:
        """Get a guild's StackOverflow tags config by ID.

        Args:
            sotags_service (SOTagsConfigService): StackOverflow tags config service
            guild_id (int): Guild ID

        Returns:
            SOTagsConfig: StackOverflow tags config object
        """
        result = await sotags_service.get(guild_id, id_attribute="guild_id")
        return sotags_service.to_schema(schema_type=SOTagsConfigSchema, data=result)

    @get(
        operation_id="AllowedUsersDetail",
        name="guilds:allowed-users-config",
        summary="Get allowed users config for a guild.",
        path=urls.GUILD_ALLOWED_USERS_DETAIL,
    )
    async def get_guild_allowed_users_config(
        self,
        allowed_users_service: AllowedUsersConfigService,
        guild_id: int = Parameter(
            title="Guild ID",
            description="The guild ID.",
        ),
    ) -> AllowedUsersConfigSchema | OffsetPagination[AllowedUsersConfigSchema]:
        """Get a guild's allowed users config by ID.

        Args:
            allowed_users_service (AllowedUsersConfigService): Allowed users config service
            guild_id (int): Guild ID

        Returns:
            AllowedUsersConfig: Allowed users config object
        """
        result = await allowed_users_service.get(guild_id, id_attribute="guild_id")
        return allowed_users_service.to_schema(schema_type=AllowedUsersConfigSchema, data=result)

    @get(
        operation_id="ForumDetail",
        name="guilds:forum-config",
        summary="Get forum config for a guild.",
        path=urls.GUILD_FORUM_DETAIL,
    )
    async def get_guild_forum_config(
        self,
        forum_service: ForumConfigService,
        guild_id: int = Parameter(
            title="Guild ID",
            description="The guild ID.",
        ),
    ) -> ForumConfigSchema | OffsetPagination[ForumConfigSchema]:
        """Get a guild's forum config by ID.

        Args:
            forum_service (ForumConfigService): Forum config service
            guild_id (int): Guild ID

        Returns:
            ForumConfig: Forum config object
        """
        result = await forum_service.get(guild_id, id_attribute="guild_id")
        return forum_service.to_schema(schema_type=ForumConfigSchema, data=result)
