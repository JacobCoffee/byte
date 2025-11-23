"""Health check endpoints for orchestration and monitoring."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar import Controller, MediaType, get
from litestar.response import Response
from litestar.status_codes import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE
from sqlalchemy import text

from byte_api.lib import log

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ["HealthController"]

logger = log.get_logger()


class HealthController(Controller):
    """Health check and readiness endpoints for container orchestration."""

    path = "/health"
    opt = {"exclude_from_auth": True}

    @get(
        "/",
        operation_id="HealthCheck",
        name="health:check",
        media_type=MediaType.JSON,
        cache=False,
        tags=["Health"],
        summary="Health Check",
        description="General health check with database verification. Returns 200 if healthy, 503 if degraded.",
    )
    async def health_check(self, db_session: AsyncSession) -> Response[dict[str, Any]]:
        """Check overall service health including database.

        This endpoint provides a general health check that verifies database
        connectivity. Used by Docker healthchecks and monitoring tools.

        Args:
            db_session: Database session for connectivity check.

        Returns:
            Response with health status (200 if healthy, 503 if degraded).
        """
        try:
            await db_session.execute(text("SELECT 1"))
            logger.debug("Health check passed")
            return Response(
                content={"status": "ok", "database": "healthy"},
                status_code=HTTP_200_OK,
                media_type=MediaType.JSON,
            )
        except Exception as e:
            logger.exception("Health check failed", error=str(e))
            return Response(
                content={"status": "degraded", "database": "unhealthy"},
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                media_type=MediaType.JSON,
            )

    @get(
        "/ready",
        operation_id="ReadinessCheck",
        name="health:readiness",
        media_type=MediaType.JSON,
        cache=False,
        tags=["Health"],
        summary="Readiness Check",
        description="Kubernetes-style readiness probe. Returns 200 if service is ready to accept traffic.",
    )
    async def readiness_check(self, db_session: AsyncSession) -> Response[dict[str, Any]]:
        """Check if service is ready to accept traffic.

        This endpoint is designed for container orchestration systems like Kubernetes
        to determine if the service should receive traffic. It verifies critical
        dependencies like database connectivity.

        Args:
            db_session: Database session for connectivity check.

        Returns:
            Response with ready status (200) or service unavailable (503).

        Raises:
            Exception: If database is unreachable, returns 503.
        """
        try:
            await db_session.execute(text("SELECT 1"))
            logger.debug("Readiness check passed")
            return Response(
                content={"status": "ready"},
                status_code=HTTP_200_OK,
                media_type=MediaType.JSON,
            )
        except Exception as e:
            logger.exception("Readiness check failed", error=str(e))
            return Response(
                content={"status": "not_ready", "error": "database_unavailable"},
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                media_type=MediaType.JSON,
            )

    @get(
        "/live",
        operation_id="LivenessCheck",
        name="health:liveness",
        media_type=MediaType.JSON,
        cache=False,
        tags=["Health"],
        summary="Liveness Check",
        description="Kubernetes-style liveness probe. Returns 200 if service is alive and not deadlocked.",
    )
    async def liveness_check(self) -> Response[dict[str, str]]:
        """Check if service is alive.

        This endpoint is designed for container orchestration systems like Kubernetes
        to determine if the service is alive and not deadlocked. It performs minimal
        checks to avoid false positives.

        Returns:
            Response with alive status (always 200 unless service is completely dead).
        """
        logger.debug("Liveness check passed")
        return Response(
            content={"status": "alive"},
            status_code=HTTP_200_OK,
            media_type=MediaType.JSON,
        )
