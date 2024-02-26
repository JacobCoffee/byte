"""System domain helper functions."""
from __future__ import annotations

from time import time
from typing import TYPE_CHECKING

from sqlalchemy import text

__all__ = ("check_byte_status", "check_database_status")


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from server.lib.types import Status

DEGRADED_THRESHOLD = 2.0
"""float: Threshold in seconds for degraded status."""


async def check_database_status(db_session: AsyncSession) -> Status:
    """Check database health.

    Args:
        db_session (AsyncSession): Database session.

    Returns:
        Status: Database status.
    """
    try:
        start_time = time()
        await db_session.execute(text("select 1"))
        end_time = time()
        response_time = end_time - start_time
        if response_time > DEGRADED_THRESHOLD:
            return "degraded"
    except ConnectionRefusedError:
        return "offline"
    return "online"


async def check_byte_status() -> Status:
    """Check Byte status.

    .. todo:: This is a stub. Need to figure out how to
        call the current bot instance from here.

        async def healthcheck(self) -> Status:
            latency = round(self.bot.latency * 1000, 2)
            ratelimited = self.bot.is_ws_ratelimited()
            ready = self.bot.is_ready()
            if closed := self.bot.is_closed():
                return "offline"
            latency_threshold = 1000
            # noinspection PyTypeChecker
            return "degraded" if not ready or ratelimited or latency > latency_threshold else "online"

    Returns:
        Status: Byte status.
    """
    return "offline"
