"""Dependencies for guilds."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import joinedload, noload, selectinload

from server.domain.db.models import AllowedUsersConfig, GitHubConfig, Guild, SOTagsConfig
from server.domain.guilds.services import (
    GuildService,
)
from server.lib import log

__all__ = ("provides_guild_config_service",)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession

logger = log.get_logger()


async def provides_guild_config_service(db_session: AsyncSession) -> AsyncGenerator[GuildService, None]:
    """Construct Guild-based repository and service objects for the request.

    Args:
        db_session (AsyncSession): SQLAlchemy AsyncSession

    Yields:
        GuildService: Guild-based service
    """
    async with GuildService.new(
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
            yield service
        finally:
            ...
