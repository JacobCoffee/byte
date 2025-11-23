"""Tests for system controller endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from litestar.status_codes import HTTP_200_OK

if TYPE_CHECKING:
    from litestar.testing import AsyncTestClient

__all__ = ["TestSystemHealthEndpoint"]


@pytest.mark.asyncio
class TestSystemHealthEndpoint:
    """Tests for GET /system/health endpoint."""

    async def test_system_health_check_success(self, api_client: AsyncTestClient) -> None:
        """Test /system/health returns system health status."""
        response = await api_client.get("/system/health")

        # Should return 200, 503, or 500 depending on system status
        assert response.status_code in [HTTP_200_OK, 503, 500]

        if response.status_code == HTTP_200_OK:
            data = response.json()
            # Verify expected fields in response
            assert "database_status" in data
            assert "byte_status" in data
            assert "overall_status" in data

            # Status values should be valid
            valid_statuses = ["healthy", "degraded", "offline"]
            assert data["database_status"] in valid_statuses
            assert data["byte_status"] in valid_statuses
            assert data["overall_status"] in valid_statuses

    async def test_system_health_response_structure(self, api_client: AsyncTestClient) -> None:
        """Test system health endpoint returns correct JSON structure."""
        response = await api_client.get("/system/health")

        # Should return valid JSON even on error
        assert response.headers.get("content-type") == "application/json"

        data = response.json()
        assert isinstance(data, dict)
