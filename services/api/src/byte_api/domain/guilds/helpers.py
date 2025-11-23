"""Helper functions to be used for interacting with Guild data."""

from __future__ import annotations

from byte_api.domain.guilds.dependencies import provides_guilds_service
from byte_api.lib.db import config

__all__ = ("get_byte_server_count",)


async def get_byte_server_count() -> int:
    """Get the server count for Byte.

    Returns:
        int: The server counts for Byte or 0 if there are none.
    """
    async with config.get_session() as session:
        guilds_service = await anext(provides_guilds_service(db_session=session))
        total = await guilds_service.count()
        return total or 0
