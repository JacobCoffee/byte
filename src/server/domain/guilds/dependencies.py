"""Dependencies for guilds."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import joinedload, noload, selectinload

from server.domain.db.models import (
    GitHubConfig,
    GuildConfig,
    GuildGitHubConfig,
)
from server.domain.guilds.services import GuildsService
from server.lib import log

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ("provides_guilds_service",)

logger = log.get_logger()


async def provides_guilds_service(db_session: AsyncSession) -> AsyncGenerator[GuildsService, None]:
    """Construct GuildConfig-based repository and service objects for the request.

    Args:
        db_session (AsyncSession): SQLAlchemy AsyncSession

    Yields:
        GuildsService: GuildConfig-based service
    """
    async with GuildsService.new(
        session=db_session,
        statement=select(GuildConfig)
        .order_by(GuildConfig.guild_id)
        .options(
            selectinload(GuildConfig.github_config)
            .joinedload(GuildGitHubConfig.guild_id, innerjoin=True)
            .options(
                joinedload(GitHubConfig.guild_config),
                noload("*"),
            ),
        ),
    ) as service:
        try:
            yield service
        finally:
            ...
