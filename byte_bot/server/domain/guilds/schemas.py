"""API Schemas for guild domain."""

from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from pydantic import Field

from byte_bot.server.lib.schema import CamelizedBaseModel

__all__ = ("GuildCreate", "GuildSchema", "GuildUpdate", "UpdateableGuildSetting")


class GitHubConfigSchema(CamelizedBaseModel):
    guild_id: UUID
    discussion_sync: bool
    github_organization: str | None
    github_repository: str | None


class SOTagsConfigSchema(CamelizedBaseModel):
    guild_id: UUID
    tag_name: str


class AllowedUsersConfigSchema(CamelizedBaseModel):
    guild_id: int
    user_id: UUID


class GuildSchema(CamelizedBaseModel):
    """Schema representing an existing guild."""

    internal_id: UUID = Field(title="Internal ID", description="The internal database record ID.", alias="id")
    guild_id: int = Field(title="Guild ID", description="The guild ID.")
    guild_name: str = Field(title="Name", description="The guild name.")
    prefix: str | None = Field(title="Prefix", description="The prefix for the guild.")
    help_channel_id: int | None = Field(title="Help Channel ID", description="The channel ID for the help channel.")
    sync_label: str | None = Field(
        title="Sync Label", description="The forum label to use for GitHub discussion syncs."
    )
    issue_linking: bool | None = Field(title="Issue Linking", description="Is issue linking enabled.")
    comment_linking: bool | None = Field(title="Comment Linking", description="Is comment linking enabled.")
    pep_linking: bool | None = Field(title="PEP Linking", description="Is PEP linking enabled.")
    github_config: GitHubConfigSchema | None = Field(
        title="GitHub Config", description="The GitHub configuration for the guild."
    )
    sotags_configs: list[SOTagsConfigSchema] = Field(
        title="StackOverflow Tags Configs", description="The StackOverflow tags configuration for the guild."
    )
    allowed_users: list[AllowedUsersConfigSchema] = Field(
        title="Allowed Users", description="The allowed users configuration for the guild."
    )


class GuildCreate(CamelizedBaseModel):
    """Schema representing a guild create request.

    .. todo:: Add owner ID
    """

    guild_id: int = Field(title="Guild ID", description="The guild ID.", alias="id")
    name: str = Field(title="Name", description="The guild name.")


class GuildUpdate(CamelizedBaseModel):
    """Schema representing a guild update request."""

    guild_id: int = Field(title="Guild ID", description="The guild ID.", alias="id")
    prefix: str | None = Field(title="Prefix", description="The prefix for the guild.")
    help_channel_id: int | None = Field(title="Help Channel ID", description="The channel ID for the help channel.")
    sync_label: str | None = Field(
        title="Sync Label", description="The forum label to use for GitHub discussion syncs."
    )
    issue_linking: bool | None = Field(title="Issue Linking", description="Is issue linking enabled.")
    comment_linking: bool | None = Field(title="Comment Linking", description="Is comment linking enabled.")
    pep_linking: bool | None = Field(title="PEP Linking", description="Is PEP linking enabled.")


class UpdateableGuildSetting(CamelizedBaseModel):
    """An allowed setting that admins can update for their guild."""

    """Guild Model Settings"""
    prefix: str = Field(title="Prefix", description="The prefix for the guild.")
    help_channel_id: int = Field(title="Help Channel ID", description="The channel ID for the help forum.")
    showcase_channel_id: int = Field(title="Showcase Channel ID", description="The channel ID for the showcase forum.")
    sync_label: str = Field(title="Sync Label", description="The forum label to use for GitHub discussion syncs.")
    issue_linking: bool = Field(title="Issue Linking", description="Is issue linking enabled.")
    comment_linking: bool = Field(title="Comment Linking", description="Is comment linking enabled.")
    pep_linking: bool = Field(title="PEP Linking", description="Is PEP linking enabled.")

    """GitHub Config Settings"""
    discussion_sync: bool = Field(title="Discussion Sync", description="Is GitHub discussion sync enabled.")
    github_organization: str = Field(title="GitHub Organization", description="The GitHub organization to sync.")
    github_repository: str = Field(title="GitHub Repository", description="The GitHub repository to sync.")

    """StackOverflow Tags Config Settings"""
    tag_name: list[str] = Field(
        title="StackOverflow Tag(s)",
        description="The StackOverflow tag(s) to sync.",
        examples=["litestar", "byte", "python"],
    )

    """Allowed Users Config Settings"""
    user_id: int = Field(title="User ID", description="The user or role ID to allow.")

    """Forum Config Settings"""
    """Help Forum"""
    help_forum: bool = Field(title="Help Forum", description="Is the help forum enabled.")
    help_forum_category: str = Field(title="Help Forum Category", description="The help forum category.")
    help_thread_auto_close: bool = Field(
        title="Help Thread Auto Close", description="Is the help thread auto close enabled."
    )
    help_thread_auto_close_days: int = Field(
        title="Help Thread Auto Close Days", description="The days to auto close help threads after inactivity."
    )
    help_thread_notify: bool = Field(
        title="Help Thread Notify", description="Whether to notify roles for unresponded help threads."
    )
    help_thread_notify_roles: list[int] = Field(
        title="Help Thread Notify Roles", description="The roles to notify for unresponded help threads."
    )
    help_thread_notify_days: int = Field(
        title="Help Thread Notify Days", description="The days to notify `notify_roles` after not receiving a response."
    )
    help_thread_sync: bool = Field(
        title="Help Thread Sync", description="Is the help thread GitHub discussions sync enabled."
    )

    """Showcase forum"""
    showcase_forum: bool = Field(title="Showcase Forum", description="Is the showcase forum enabled.")
    showcase_forum_category: str = Field(title="Showcase Forum Category", description="The showcase forum category.")
    showcase_thread_auto_close: bool = Field(
        title="Showcase Thread Auto Close", description="Is the showcase thread auto close enabled."
    )
    showcase_thread_auto_close_days: int = Field(
        title="Showcase Thread Auto Close Days", description="The days to auto close showcase threads after inactivity."
    )
