"""Dependencies for guilds."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import joinedload, noload, selectinload

from byte_bot.server.domain.db.models import AllowedUsersConfig, ForumConfig, GitHubConfig, Guild, SOTagsConfig
from byte_bot.server.domain.guilds.services import GuildsService
from byte_bot.server.lib import log

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ("provides_guilds_service",)

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
            yield service
        finally:
            ...
