"""Dependencies for guilds."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import joinedload, noload, selectinload

from src.server.domain.db.models import GuildAllowedUsersConfig, GuildConfig, GuildGitHubConfig, GuildSOTagsConfig
from src.server.domain.guilds.services import (
    GuildConfigService,
)
from src.server.lib import log

__all__ = ("provides_guild_config_service",)


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession

logger = log.get_logger()


async def provides_guild_config_service(db_session: AsyncSession) -> AsyncGenerator[GuildConfigService, None]:
    """Construct GuildConfig-based repository and service objects for the request.

    Args:
        db_session (AsyncSession): SQLAlchemy AsyncSession

    Yields:
        GuildConfigService: GuildConfig-based service
    """
    async with GuildConfigService.new(
        session=db_session,
        statement=select(GuildConfig)
        .order_by(GuildConfig.guild_name)
        .options(
            selectinload(GuildConfig.github_config).options(
                joinedload(GuildGitHubConfig.guild_name, innerjoin=True).options(noload("*")),
            ),
            selectinload(GuildConfig.sotags_config).options(
                joinedload(GuildSOTagsConfig.guild_name, innerjoin=True).options(noload("*")),
            ),
            selectinload(GuildConfig.allowed_users_config).options(
                joinedload(GuildAllowedUsersConfig.guild_name, innerjoin=True).options(noload("*")),
            ),
        ),
    ) as service:
        try:
            yield service
        finally:
            ...
