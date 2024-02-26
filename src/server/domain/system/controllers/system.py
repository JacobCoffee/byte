"""System Controller."""
from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, MediaType, get
from litestar.response import Response

from server.domain import urls
from server.domain.system.dtos import SystemHealth
from server.domain.system.helpers import check_byte_status, check_database_status
from server.lib import log

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ["SystemController"]

logger = log.get_logger()


class SystemController(Controller):
    """System Controller."""

    opt = {"exclude_from_auth": True}

    @get(
        operation_id="SystemHealth",
        name="system:health",
        path=urls.SYSTEM_HEALTH,
        media_type=MediaType.JSON,
        cache=False,
        tags=["System"],
        summary="Health Check",
        description="Execute a health check against backend components including database and bot status.",
        signature_namespace={"SystemHealth": SystemHealth},
    )
    async def check_system_health(self, db_session: AsyncSession) -> Response[SystemHealth]:
        """Check the overall system health.

        Args:
            db_session (AsyncSession): Database session.

        Returns:
            Response[SystemHealth]: System health.
        """
        database_status = await check_database_status(db_session)
        byte_status = await check_byte_status()
        statuses = [database_status, byte_status]

        if all(status == "offline" for status in statuses):
            overall_status = "offline"
        elif "offline" in statuses or "degraded" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        status_code = 200 if overall_status == "healthy" else 503 if overall_status == "degraded" else 500
        # noinspection PyTypeChecker
        system_health_detail = SystemHealth(
            database_status=database_status,
            byte_status=byte_status,
            overall_status=overall_status,
        )

        return Response(
            content=system_health_detail,
            status_code=status_code,
            media_type=MediaType.JSON,
        )
