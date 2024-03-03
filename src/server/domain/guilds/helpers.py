"""Helper functions to be used for interacting with Guild data."""
from __future__ import annotations

from server.domain.guilds.dependencies import provides_guilds_service
from server.lib.db import config

__all__ = ("get_byte_server_count",)


async def get_byte_server_count() -> int:
    """Get the server count for Byte.

    Returns:
        int: The server count for Byte.
    """
    async with config.get_session() as session:
        guilds_service = await anext(provides_guilds_service(db_session=session))
        _, total = await guilds_service.list_and_count()

        return total or 0
