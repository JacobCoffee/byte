"""Dependencies for guilds."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from src.server.domain.db.models import Guild
from src.server.domain.guilds.services import GuildsService
from src.server.lib import log

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
    async with GuildsService.new(session=db_session, statement=select(Guild).order_by(Guild.guild_id)) as service:
        try:
            yield service
        finally:
            ...
