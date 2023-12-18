"""API Schemas for guild domain."""
from __future__ import annotations

from pydantic import Field

from server.lib.schema import CamelizedBaseModel

__all__ = ("GuildCreate", "GuildSchema", "GuildUpdate")


class GuildSchema(CamelizedBaseModel):
    """Schema representing an existing guild."""

    guild_id: int = Field(title="Guild ID", description="The guild ID.", alias="id")
    name: str = Field(title="Name", description="The guild name.")
    prefix: str | None = Field(title="Prefix", description="The prefix for the guild.")
    help_channel_id: int | None = Field(title="Help Channel ID", description="The channel ID for the help channel.")
    sync_label: str | None = Field(
        title="Sync Label", description="The forum label to use for GitHub discussion syncs."
    )
    issue_linking: bool | None = Field(title="Issue Linking", description="Is issue linking enabled.")
    comment_linking: bool | None = Field(title="Comment Linking", description="Is comment linking enabled.")
    pep_linking: bool | None = Field(title="PEP Linking", description="Is PEP linking enabled.")


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
