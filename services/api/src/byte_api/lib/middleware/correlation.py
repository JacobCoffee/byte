"""Correlation ID middleware for request tracing.

This middleware extracts or generates correlation IDs for each HTTP request,
adds them to structured logs, and includes them in response headers.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import structlog
from litestar.datastructures import MutableScopeHeaders

if TYPE_CHECKING:
    from litestar.types import ASGIApp, Receive, Scope, Send

__all__ = ["correlation_middleware"]

logger = structlog.get_logger()


def correlation_middleware(app: ASGIApp) -> ASGIApp:
    """Middleware factory for correlation ID tracking.

    Args:
        app: The ASGI application

    Returns:
        ASGI middleware that handles correlation IDs
    """

    async def middleware(scope: Scope, receive: Receive, send: Send) -> None:
        """Add correlation ID to requests and logs.

        This middleware:
        - Extracts X-Correlation-ID from request headers or generates new UUID
        - Adds correlation_id to all structured logs in this request
        - Includes X-Correlation-ID in response headers
        - Makes correlation_id available in route handlers via scope

        Args:
            scope: The connection scope
            receive: The receive channel
            send: The send channel
        """
        if scope["type"] != "http":
            await app(scope, receive, send)
            return

        headers = MutableScopeHeaders(scope)
        correlation_id = headers.get("x-correlation-id") or str(uuid.uuid4())

        # Add to scope for access in route handlers
        scope["correlation_id"] = correlation_id

        # Bind to structlog context for this request
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        async def send_wrapper(message: dict) -> None:
            """Add correlation ID to response headers.

            Args:
                message: The ASGI message
            """
            if message["type"] == "http.response.start":
                response_headers = MutableScopeHeaders.from_message(message)
                response_headers["x-correlation-id"] = correlation_id
            await send(message)

        try:
            await app(scope, receive, send_wrapper)
        finally:
            # Clear context after request
            structlog.contextvars.clear_contextvars()

    return middleware
