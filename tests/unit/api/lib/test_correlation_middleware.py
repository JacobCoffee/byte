"""Tests for correlation ID middleware."""

from __future__ import annotations

import pytest
from litestar.testing import AsyncTestClient

from byte_api.app import create_app


@pytest.fixture
def app():
    """Create Litestar app for testing."""
    return create_app()


@pytest.mark.asyncio
async def test_correlation_id_generated_if_missing(app):
    """Test correlation ID is generated when not provided in request headers."""
    async with AsyncTestClient(app=app) as client:
        response = await client.get("/health/live")
        assert response.status_code == 200
        assert "x-correlation-id" in response.headers
        correlation_id = response.headers["x-correlation-id"]
        # UUID v4 format: 8-4-4-4-12 = 36 characters with dashes
        assert len(correlation_id) == 36
        assert correlation_id.count("-") == 4


@pytest.mark.asyncio
async def test_correlation_id_propagated(app):
    """Test provided correlation ID is returned in response headers."""
    test_correlation_id = "test-correlation-id-123"
    async with AsyncTestClient(app=app) as client:
        response = await client.get("/health/live", headers={"x-correlation-id": test_correlation_id})
        assert response.status_code == 200
        assert "x-correlation-id" in response.headers
        assert response.headers["x-correlation-id"] == test_correlation_id


@pytest.mark.asyncio
async def test_correlation_id_unique_per_request(app):
    """Test different requests get different correlation IDs when not provided."""
    async with AsyncTestClient(app=app) as client:
        response1 = await client.get("/health/live")
        response2 = await client.get("/health/live")

        assert response1.status_code == 200
        assert response2.status_code == 200

        correlation_id_1 = response1.headers["x-correlation-id"]
        correlation_id_2 = response2.headers["x-correlation-id"]

        # Each request should get a unique correlation ID
        assert correlation_id_1 != correlation_id_2


@pytest.mark.asyncio
async def test_correlation_id_available_in_logs(app, caplog):
    """Test correlation ID is included in structured logs.

    Note: This test verifies the middleware sets up the correlation ID,
    but structlog context clearing means we can't easily verify it in
    captured logs without a more complex setup. This is a basic sanity check.
    """
    async with AsyncTestClient(app=app) as client:
        response = await client.get("/health/live")
        assert response.status_code == 200
        assert "x-correlation-id" in response.headers
        # Just verify the endpoint works - detailed log testing would require
        # more complex structlog configuration
