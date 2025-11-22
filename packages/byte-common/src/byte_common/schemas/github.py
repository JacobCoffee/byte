"""GitHub configuration schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

__all__ = ("CreateGitHubConfigRequest", "GitHubConfigSchema", "UpdateGitHubConfigRequest", )


class GitHubConfigSchema(BaseModel):
    """GitHub configuration schema for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    guild_id: int
    discussion_sync: bool = False
    github_organization: str | None = None
    github_repository: str | None = None


class CreateGitHubConfigRequest(BaseModel):
    """Request schema for creating a GitHub configuration."""

    guild_id: int = Field(..., description="Discord guild ID")
    discussion_sync: bool = Field(default=False, description="Enable discussion sync")
    github_organization: str | None = Field(default=None, description="GitHub organization")
    github_repository: str | None = Field(default=None, description="GitHub repository")


class UpdateGitHubConfigRequest(BaseModel):
    """Request schema for updating a GitHub configuration."""

    discussion_sync: bool | None = Field(default=None, description="Enable discussion sync")
    github_organization: str | None = Field(default=None, description="GitHub organization")
    github_repository: str | None = Field(default=None, description="GitHub repository")
