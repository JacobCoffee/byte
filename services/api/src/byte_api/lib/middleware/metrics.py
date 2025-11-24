"""Metrics middleware for automatic HTTP request tracking.

This middleware tracks all HTTP requests with Prometheus metrics including
request counts, latency histograms, and error rates.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from byte_api.domain.system.controllers.metrics import http_request_duration_seconds, http_requests_total

if TYPE_CHECKING:
    from litestar.types import ASGIApp, Receive, Scope, Send

__all__ = ["metrics_middleware"]


def metrics_middleware(app: ASGIApp) -> ASGIApp:
    """Middleware factory for Prometheus metrics tracking.

    Args:
        app: The ASGI application

    Returns:
        ASGI middleware that tracks HTTP metrics
    """

    async def middleware(scope: Scope, receive: Receive, send: Send) -> None:
        """Track HTTP request metrics.

        This middleware automatically tracks:
        - Request counts by method, endpoint, and status code
        - Request latency by method and endpoint

        Args:
            scope: The connection scope
            receive: The receive channel
            send: The send channel
        """
        if scope["type"] != "http":
            await app(scope, receive, send)
            return

        start_time = time.time()

        # Track request
        method = scope["method"]
        path = scope["path"]

        status_code = 500  # Default to error if something goes wrong

        async def send_wrapper(message: dict) -> None:
            """Capture status code from response.

            Args:
                message: The ASGI message
            """
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await app(scope, receive, send_wrapper)
        finally:
            # Calculate duration and record metrics
            duration = time.time() - start_time
            http_request_duration_seconds.labels(method=method, endpoint=path).observe(duration)
            http_requests_total.labels(method=method, endpoint=path, status=status_code).inc()

    return middleware
