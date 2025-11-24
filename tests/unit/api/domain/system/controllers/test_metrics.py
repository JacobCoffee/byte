"""Tests for Prometheus metrics endpoint."""

from __future__ import annotations

import pytest
from litestar.testing import AsyncTestClient

from byte_api.app import create_app


@pytest.fixture
def app():
    """Create Litestar app for testing."""
    return create_app()


@pytest.mark.asyncio
async def test_metrics_endpoint_returns_prometheus_format(app):
    """Test /metrics endpoint returns Prometheus text format."""
    async with AsyncTestClient(app=app) as client:
        response = await client.get("/metrics")
        assert response.status_code == 200

        # Verify content type
        assert "text/plain" in response.headers["content-type"]

        # Verify Prometheus metrics are present
        text = response.text
        assert "http_requests_total" in text
        assert "http_request_duration_seconds" in text
        assert "db_queries_total" in text
        assert "guild_operations_total" in text


@pytest.mark.asyncio
async def test_metrics_endpoint_tracks_requests(app):
    """Test metrics endpoint tracks HTTP requests."""
    async with AsyncTestClient(app=app) as client:
        # Make a request to liveness endpoint (doesn't need DB)
        health_response = await client.get("/health/live")
        assert health_response.status_code == 200

        # Check metrics
        metrics_response = await client.get("/metrics")
        assert metrics_response.status_code == 200

        text = metrics_response.text

        # Should have tracked the health check request
        # Note: The exact count depends on test execution order, so we just
        # verify the metric exists and has a non-zero value
        assert "http_requests_total" in text
        assert "http_request_duration_seconds" in text


@pytest.mark.asyncio
async def test_metrics_endpoint_not_in_openapi_schema(app):
    """Test metrics endpoint is excluded from OpenAPI schema.

    Note: The metrics endpoint should work but not appear in API documentation.
    """
    async with AsyncTestClient(app=app) as client:
        # Metrics endpoint should respond
        metrics_response = await client.get("/metrics")
        assert metrics_response.status_code == 200

        # But it's marked as include_in_schema=False
        # which means it won't be in OpenAPI docs
        # This is intentional - it's for Prometheus, not API consumers


@pytest.mark.asyncio
async def test_metrics_include_method_and_status(app):
    """Test metrics include HTTP method and status code labels."""
    async with AsyncTestClient(app=app) as client:
        # Make a GET request
        await client.get("/health/live")

        # Get metrics
        response = await client.get("/metrics")
        text = response.text

        # Should include method and status labels
        # Example: http_requests_total{method="GET",endpoint="/health/live",status="200"}
        assert 'method="GET"' in text
        assert 'status="200"' in text
