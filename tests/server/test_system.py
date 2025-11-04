"""Tests for system controller (health checks, status)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

if TYPE_CHECKING:
    from litestar.testing import AsyncTestClient

__all__ = ("TestSystemController",)


@pytest.mark.skip(reason="Requires full app setup with test database")
class TestSystemController:
    """Test suite for System Controller endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncTestClient) -> None:
        """Test health check endpoint.

        Args:
            client: Test HTTP client
        """
        response = await client.get("/health")

        assert response.status_code in (HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE)
        # Health check may return 503 if database isn't ready in test environment

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_json(self, client: AsyncTestClient) -> None:
        """Test that health endpoint returns JSON data.

        Args:
            client: Test HTTP client
        """
        response = await client.get("/health")

        assert response.headers["content-type"].startswith("application/json")
        data = response.json()
        assert isinstance(data, dict)
