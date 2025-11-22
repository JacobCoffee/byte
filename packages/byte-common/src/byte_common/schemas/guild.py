"""Guild schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GuildSchema(BaseModel):
    """Guild schema for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    guild_id: int
    guild_name: str
    prefix: str = "!"
    help_channel_id: int | None = None
    showcase_channel_id: int | None = None
    sync_label: str | None = None
    issue_linking: bool = False
    comment_linking: bool = False
    pep_linking: bool = False


class CreateGuildRequest(BaseModel):
    """Request schema for creating a guild."""

    guild_id: int = Field(..., description="Discord guild ID")
    guild_name: str = Field(..., min_length=1, max_length=100, description="Discord guild name")
    prefix: str = Field(default="!", min_length=1, max_length=5, description="Command prefix")
    help_channel_id: int | None = Field(default=None, description="Help channel ID")
    showcase_channel_id: int | None = Field(default=None, description="Showcase channel ID")
    sync_label: str | None = Field(default=None, description="GitHub sync label")
    issue_linking: bool = Field(default=False, description="Enable GitHub issue linking")
    comment_linking: bool = Field(default=False, description="Enable GitHub comment linking")
    pep_linking: bool = Field(default=False, description="Enable PEP linking")


class UpdateGuildRequest(BaseModel):
    """Request schema for updating a guild."""

    guild_name: str | None = Field(default=None, min_length=1, max_length=100, description="Discord guild name")
    prefix: str | None = Field(default=None, min_length=1, max_length=5, description="Command prefix")
    help_channel_id: int | None = Field(default=None, description="Help channel ID")
    showcase_channel_id: int | None = Field(default=None, description="Showcase channel ID")
    sync_label: str | None = Field(default=None, description="GitHub sync label")
    issue_linking: bool | None = Field(default=None, description="Enable GitHub issue linking")
    comment_linking: bool | None = Field(default=None, description="Enable GitHub comment linking")
    pep_linking: bool | None = Field(default=None, description="Enable PEP linking")
