"""Prometheus metrics endpoint and metric definitions.

This module defines all Prometheus metrics for the API service and provides
an endpoint for Prometheus to scrape.
"""

from __future__ import annotations

from litestar import Controller, get
from litestar.response import Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Histogram, generate_latest

__all__ = [
    "MetricsController",
    "db_queries_total",
    "guild_operations_total",
    "http_request_duration_seconds",
    "http_requests_total",
    "registry",
]

# Create registry for all metrics
registry = CollectorRegistry()

# HTTP request metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=registry,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    registry=registry,
)

# Database metrics
db_queries_total = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation"],
    registry=registry,
)

# Business metrics
guild_operations_total = Counter(
    "guild_operations_total",
    "Total guild operations",
    ["operation", "status"],
    registry=registry,
)


class MetricsController(Controller):
    """Prometheus metrics endpoint for monitoring."""

    path = "/metrics"
    opt = {"exclude_from_auth": True}

    @get(
        "/",
        operation_id="PrometheusMetrics",
        name="metrics:prometheus",
        include_in_schema=False,
        tags=["System"],
        summary="Prometheus Metrics",
        description="Prometheus metrics endpoint for scraping. Returns metrics in Prometheus text format.",
    )
    async def metrics_endpoint(self) -> Response:
        """Prometheus metrics endpoint.

        Returns:
            Response: Prometheus metrics in text format

        Note:
            This endpoint is not included in the OpenAPI schema as it's
            intended for Prometheus scraping, not general API consumption.
        """
        metrics_data = generate_latest(registry)
        return Response(
            content=metrics_data,
            media_type=CONTENT_TYPE_LATEST,
        )
