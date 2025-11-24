"""WebSocket controller for real-time dashboard updates."""

from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import structlog
from litestar import WebSocket, websocket
from litestar.exceptions import WebSocketDisconnect
from sqlalchemy import func, select

from byte_common.models.guild import Guild

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


logger = structlog.get_logger()

__all__ = ("dashboard_stream",)

# Track application startup time for uptime calculation
_startup_time: datetime | None = None

# WebSocket update interval (configurable for testing)
UPDATE_INTERVAL = float(os.getenv("WS_UPDATE_INTERVAL", "5.0"))


def set_startup_time() -> None:
    """Set the application startup time (call from app.on_startup)."""
    global _startup_time  # noqa: PLW0603
    _startup_time = datetime.now(UTC)
    logger.info("Application startup time recorded", startup_time=_startup_time.isoformat())


def get_uptime_seconds() -> int:
    """Get application uptime in seconds.

    Returns:
        int: Uptime in seconds since application start. Returns 0 if startup time not set.
    """
    if _startup_time is None:
        return 0
    delta = datetime.now(UTC) - _startup_time
    return int(delta.total_seconds())


async def get_server_count(db_session: AsyncSession) -> int:
    """Get current server/guild count from database.

    Args:
        db_session: Database session for querying guilds.

    Returns:
        int: Number of guilds in the database.
    """
    result = await db_session.execute(select(func.count()).select_from(Guild))
    return result.scalar_one()


@websocket("/ws/dashboard")
async def dashboard_stream(socket: WebSocket, db_session: AsyncSession) -> None:
    """Stream real-time dashboard updates via WebSocket.

    Sends JSON updates every 5 seconds containing:
    - server_count: Number of guilds
    - bot_status: online/offline
    - uptime: Seconds since startup
    - timestamp: ISO format timestamp

    Args:
        socket: WebSocket connection.
        db_session: Database session injected by Litestar.
    """
    await socket.accept()
    logger.info("Dashboard WebSocket client connected", client=socket.client)

    try:
        # Send updates in a loop
        while True:
            try:
                server_count = await get_server_count(db_session)
                uptime = get_uptime_seconds()

                data = {
                    "server_count": server_count,
                    "bot_status": "online",
                    "uptime": uptime,
                    "timestamp": datetime.now(UTC).isoformat(),
                }

                await socket.send_json(data)
                logger.debug("Sent dashboard update", data=data)

                # Sleep - any send failures will be caught and exit loop
                await asyncio.sleep(UPDATE_INTERVAL)

            except (WebSocketDisconnect, RuntimeError):
                # Client disconnected or connection closed
                logger.info("WebSocket client disconnected")
                break

    except asyncio.CancelledError:
        # Task was cancelled (e.g., test cleanup)
        logger.info("WebSocket handler cancelled")
        raise
    except WebSocketDisconnect:
        logger.info("Dashboard WebSocket client disconnected", client=socket.client)
    except Exception:
        logger.exception("WebSocket error occurred")
        raise
