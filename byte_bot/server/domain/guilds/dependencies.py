"""Dependencies for guilds."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import joinedload, noload, selectinload

from byte_bot.server.domain.db.models import AllowedUsersConfig, ForumConfig, GitHubConfig, Guild, SOTagsConfig
from byte_bot.server.domain.guilds.services import (
    AllowedUsersConfigService,
    ForumConfigService,
    GitHubConfigService,
    GuildsService,
    SOTagsConfigService,
)
from byte_bot.server.lib import log

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = (
    "provides_allowed_users_config_service",
    "provides_forum_config_service",
    "provides_github_config_service",
    "provides_guilds_service",
    "provides_sotags_config_service",
)

logger = log.get_logger()


async def provides_guilds_service(db_session: AsyncSession) -> AsyncGenerator[GuildsService, None]:
    """Construct Guilds-based repository and service objects for the request.

    Args:
        db_session (AsyncSession): SQLAlchemy AsyncSession

    Yields:
        GuildsService: GuildConfig-based service
    """
    async with GuildsService.new(
        session=db_session,
        statement=select(Guild)
        .order_by(Guild.guild_name)
        .options(
            selectinload(Guild.github_config).options(
                joinedload(GitHubConfig.guild, innerjoin=True).options(noload("*")),
            ),
            selectinload(Guild.sotags_configs).options(
                joinedload(SOTagsConfig.guild, innerjoin=True).options(noload("*")),
            ),
            selectinload(Guild.allowed_users).options(
                joinedload(AllowedUsersConfig.guild, innerjoin=True).options(noload("*")),
            ),
            selectinload(Guild.forum_config).options(
                joinedload(ForumConfig.guild, innerjoin=True).options(noload("*")),
            ),
        ),
    ) as service:
        try:
            yield service  # type: ignore[misc]
        finally:
            ...


async def provides_github_config_service(db_session: AsyncSession) -> AsyncGenerator[GitHubConfigService, None]:  # type: ignore[misc]
    """Construct GitHubConfig-based repository and service objects for the request.

    Args:
        db_session (AsyncSession): SQLAlchemy AsyncSession

    Yields:
        GitHubConfigService: GitHubConfig-based service
    """
    async with GuildsService.new(
        session=db_session,
        statement=select(Guild)
        .order_by(Guild.guild_name)
        .options(
            selectinload(Guild.github_config).options(
                joinedload(GitHubConfig.guild, innerjoin=True).options(noload("*")),
            ),
            selectinload(Guild.sotags_configs).options(
                joinedload(SOTagsConfig.guild, innerjoin=True).options(noload("*")),
            ),
            selectinload(Guild.allowed_users).options(
                joinedload(AllowedUsersConfig.guild, innerjoin=True).options(noload("*")),
            ),
        ),
    ) as service:
        try:
            yield service  # type: ignore[misc]
        finally:
            ...


async def provides_sotags_config_service(db_session: AsyncSession) -> AsyncGenerator[SOTagsConfigService, None]:
    """Construct SOTagsConfig-based repository and service objects for the request.

    Args:
        db_session (AsyncSession): SQLAlchemy AsyncSession

    Yields:
        SOTagsConfigService: SOTagsConfig-based service
    """
    async with SOTagsConfigService.new(
        session=db_session,
        statement=select(SOTagsConfig)
        .order_by(SOTagsConfig.tag_name)
        .options(
            selectinload(SOTagsConfig.guild).options(noload("*")),
        ),
    ) as service:
        try:
            yield service  # type: ignore[misc]
        finally:
            ...


async def provides_allowed_users_config_service(
    db_session: AsyncSession,
) -> AsyncGenerator[AllowedUsersConfigService, None]:
    """Construct AllowedUsersConfig-based repository and service objects for the request.

    Args:
        db_session (AsyncSession): SQLAlchemy AsyncSession

    Yields:
        AllowedUsersConfigService: AllowedUsersConfig-based service
    """
    async with AllowedUsersConfigService.new(
        session=db_session,
        statement=select(AllowedUsersConfig)
        .order_by(AllowedUsersConfig.user_id)
        .options(
            selectinload(AllowedUsersConfig.guild).options(noload("*")),
        ),
    ) as service:
        try:
            yield service  # type: ignore[misc]
        finally:
            ...


async def provides_forum_config_service(db_session: AsyncSession) -> AsyncGenerator[ForumConfigService, None]:
    """Construct ForumConfig-based repository and service objects for the request.

    Args:
        db_session (AsyncSession): SQLAlchemy AsyncSession

    Yields:
        ForumConfigService: ForumConfig-based service
    """
    async with ForumConfigService.new(
        session=db_session,
        statement=select(ForumConfig)
        .order_by(ForumConfig.help_forum)
        .options(
            selectinload(ForumConfig.guild).options(noload("*")),
        ),
    ) as service:
        try:
            yield service  # type: ignore[misc]
        finally:
            ...
