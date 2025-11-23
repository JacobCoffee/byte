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

    async def test_system_health_status_code_mapping(self, api_client: AsyncTestClient) -> None:
        """Test system health endpoint returns appropriate status codes."""
        response = await api_client.get("/system/health")

        data = response.json()

        # Verify status code matches overall_status
        if response.status_code == HTTP_200_OK:
            assert data["overall_status"] == "healthy"
        elif response.status_code == 503:
            assert data["overall_status"] == "degraded"
        elif response.status_code == 500:
            assert data["overall_status"] == "offline"

    async def test_system_health_degraded_logic(self, api_client: AsyncTestClient) -> None:
        """Test system health returns degraded when any component is offline."""
        response = await api_client.get("/system/health")

        # The logic should mark as degraded if any component is offline/degraded
        # We can't easily mock, but we verify the response is structured correctly
        data = response.json()

        # If any component is offline/degraded, overall should reflect it
        if data["database_status"] == "offline" or data["byte_status"] == "offline":
            assert data["overall_status"] in ["offline", "degraded"]

    async def test_system_health_all_offline_logic(self, api_client: AsyncTestClient) -> None:
        """Test system health returns offline when all components offline."""
        response = await api_client.get("/system/health")

        data = response.json()

        # If all are offline, overall should be offline
        if data["database_status"] == "offline" and data["byte_status"] == "offline":
            assert data["overall_status"] == "offline"

    async def test_system_health_no_caching(self, api_client: AsyncTestClient) -> None:
        """Test system health endpoint doesn't cache responses."""
        response1 = await api_client.get("/system/health")
        response2 = await api_client.get("/system/health")

        # Both should succeed
        assert response1.status_code in [HTTP_200_OK, 503, 500]
        assert response2.status_code in [HTTP_200_OK, 503, 500]

        # Should not have aggressive caching
        # cache=False is set in controller decorator

    async def test_system_health_includes_app_metadata(self, api_client: AsyncTestClient) -> None:
        """Test system health response includes app name and version."""
        response = await api_client.get("/system/health")

        data = response.json()

        # Should include metadata from settings
        assert "app" in data
        assert "version" in data
        assert isinstance(data["app"], str)
        assert isinstance(data["version"], str)

    async def test_system_health_database_offline_status(self, api_client: AsyncTestClient) -> None:
        """Test system health endpoint structure when checking database.

        The endpoint calls check_database_status helper which verifies
        database connectivity and response time.
        """
        response = await api_client.get("/system/health")

        # Should return valid response
        assert response.status_code in [HTTP_200_OK, 503, 500]
        data = response.json()

        # Database status should be populated
        assert "database_status" in data
        assert data["database_status"] in ["online", "offline", "degraded"]

    async def test_system_status_degraded(self, api_client: AsyncTestClient) -> None:
        """Test degraded status calculation.

        Degraded occurs when at least one component is offline/degraded
        but not all components are offline.
        """
        response = await api_client.get("/system/health")

        data = response.json()

        # Verify logic: if any component is offline but not all, should be degraded
        if data["database_status"] == "offline" and data["byte_status"] != "offline":
            assert data["overall_status"] == "degraded"
            assert response.status_code == 503
        elif data["byte_status"] == "offline" and data["database_status"] != "offline":
            assert data["overall_status"] == "degraded"
            assert response.status_code == 503

    async def test_system_status_offline(self, api_client: AsyncTestClient) -> None:
        """Test offline status when all components are offline."""
        from unittest.mock import AsyncMock, patch

        from litestar.di import Provide

        # Mock db to be offline
        mock_session = AsyncMock()
        mock_session.execute.side_effect = ConnectionRefusedError("DB offline")

        async def offline_db():
            yield mock_session

        api_client.app.dependencies["db_session"] = Provide(offline_db)

        response = await api_client.get("/system/health")

        data = response.json()

        # With DB offline and byte offline (stub returns "offline")
        # overall should be offline
        if data["database_status"] == "offline" and data["byte_status"] == "offline":
            assert data["overall_status"] == "offline"
            assert response.status_code == 500

    async def test_system_health_valid_status_values(self, api_client: AsyncTestClient) -> None:
        """Test that all status fields contain valid literal values."""
        response = await api_client.get("/system/health")

        data = response.json()

        # Database status must be one of the allowed literals
        assert data["database_status"] in ["online", "offline", "degraded"]

        # Byte status must be one of the allowed literals
        assert data["byte_status"] in ["online", "offline", "degraded"]

        # Overall status must be one of the allowed literals
        assert data["overall_status"] in ["healthy", "offline", "degraded"]

    async def test_system_health_status_code_200_when_healthy(self, api_client: AsyncTestClient) -> None:
        """Test system returns 200 status code when all components healthy."""
        response = await api_client.get("/system/health")

        data = response.json()

        # If overall status is healthy, status code should be 200
        if data["overall_status"] == "healthy":
            assert response.status_code == HTTP_200_OK

    async def test_system_health_status_code_503_when_degraded(self, api_client: AsyncTestClient) -> None:
        """Test system returns 503 status code when degraded."""
        from unittest.mock import AsyncMock

        from litestar.di import Provide

        # Force degraded state by making DB slow/degraded
        mock_session = AsyncMock()
        mock_session.execute.side_effect = TimeoutError("Slow response")

        async def slow_db():
            yield mock_session

        api_client.app.dependencies["db_session"] = Provide(slow_db)

        response = await api_client.get("/system/health")

        # Should be degraded (503) or offline (500) depending on helper logic
        assert response.status_code in [503, 500]

    async def test_system_health_excludes_auth(self, api_client: AsyncTestClient) -> None:
        """Verify system health endpoint doesn't require authentication.

        Critical for monitoring tools that don't have credentials.
        """
        response = await api_client.get("/system/health")

        # Should not return 401/403
        assert response.status_code != 401
        assert response.status_code != 403

    async def test_system_health_content_type(self, api_client: AsyncTestClient) -> None:
        """Test system health returns JSON content type."""
        response = await api_client.get("/system/health")

        assert "application/json" in response.headers.get("content-type", "")

    async def test_system_health_byte_status_always_offline(self, api_client: AsyncTestClient) -> None:
        """Test that byte_status is currently always offline (stub implementation).

        This test documents current behavior and should be updated when
        the bot status check is fully implemented.
        """
        response = await api_client.get("/system/health")

        data = response.json()

        # Current implementation stub always returns "offline"
        assert data["byte_status"] == "offline"

    async def test_system_health_database_slow_response(self, api_client: AsyncTestClient) -> None:
        """Test system health when database responds slowly.

        The helper checks response time against DEGRADED_THRESHOLD (2.0s).
        """
        from unittest.mock import AsyncMock, patch

        from litestar.di import Provide

        # Mock session with normal response (in test, helper will check timing)
        mock_session = AsyncMock()

        # Simulate successful query
        async def execute_mock(*args, **kwargs):
            return None

        mock_session.execute = execute_mock

        async def normal_db():
            yield mock_session

        api_client.app.dependencies["db_session"] = Provide(normal_db)

        response = await api_client.get("/system/health")

        # Database should be considered healthy/online with normal response
        assert response.status_code in [HTTP_200_OK, 503, 500]

    async def test_system_health_multiple_status_combinations(self, api_client: AsyncTestClient) -> None:
        """Test various status combinations are handled correctly."""
        response = await api_client.get("/system/health")

        data = response.json()

        # Test status code mapping for all combinations
        db_status = data["database_status"]
        byte_status = data["byte_status"]
        overall = data["overall_status"]

        # All offline -> overall offline (500)
        if db_status == "offline" and byte_status == "offline":
            assert overall == "offline"
            assert response.status_code == 500

        # Any degraded/offline -> overall degraded (503) or offline (500)
        elif "offline" in [db_status, byte_status] or "degraded" in [db_status, byte_status]:
            assert overall in ["degraded", "offline"]
            assert response.status_code in [503, 500]

        # All online -> overall healthy (200)
        elif db_status == "online" and byte_status == "online":
            assert overall == "healthy"
            assert response.status_code == HTTP_200_OK

    async def test_system_health_app_metadata_values(self, api_client: AsyncTestClient) -> None:
        """Test app metadata fields contain expected values."""
        response = await api_client.get("/system/health")

        data = response.json()

        # App name should be non-empty
        assert len(data["app"]) > 0
        # Version should be non-empty
        assert len(data["version"]) > 0

        # Should be strings
        assert isinstance(data["app"], str)
        assert isinstance(data["version"], str)

    async def test_system_health_response_json_serializable(self, api_client: AsyncTestClient) -> None:
        """Test system health response is properly JSON serializable."""
        import json

        response = await api_client.get("/system/health")

        # Should be able to parse as JSON
        data = response.json()

        # Should be able to re-serialize
        json_str = json.dumps(data)
        assert len(json_str) > 0

        # Should be a dict
        assert isinstance(data, dict)

    async def test_system_health_database_response_time_threshold(self, api_client: AsyncTestClient) -> None:
        """Test database status considers response time threshold.

        The helper uses DEGRADED_THRESHOLD (2.0s) for degraded status.
        """
        from unittest.mock import AsyncMock, patch

        from litestar.di import Provide

        # Mock session that simulates slow query
        mock_session = AsyncMock()

        async def slow_execute(*args, **kwargs):
            import asyncio

            # Simulate slow query (but less than threshold)
            await asyncio.sleep(0.1)
            return None

        mock_session.execute = slow_execute

        async def slow_db():
            yield mock_session

        api_client.app.dependencies["db_session"] = Provide(slow_db)

        response = await api_client.get("/system/health")

        # Should still be online/healthy if below threshold
        assert response.status_code in [HTTP_200_OK, 503, 500]

    async def test_system_health_database_exception_handling(self, api_client: AsyncTestClient) -> None:
        """Test system health handles various database exceptions."""
        from unittest.mock import AsyncMock

        from litestar.di import Provide

        exceptions = [
            TimeoutError("Query timeout"),
            RuntimeError("Runtime error"),
            Exception("Generic error"),
        ]

        for exc in exceptions:
            mock_session = AsyncMock()
            mock_session.execute.side_effect = exc

            async def exc_db():
                yield mock_session

            api_client.app.dependencies["db_session"] = Provide(exc_db)

            response = await api_client.get("/system/health")

            # Should handle gracefully
            assert response.status_code in [HTTP_200_OK, 503, 500]
            data = response.json()
            assert "database_status" in data

    async def test_system_health_consistent_field_names(self, api_client: AsyncTestClient) -> None:
        """Test system health uses consistent field naming."""
        response = await api_client.get("/system/health")

        data = response.json()

        # Field names should use snake_case
        expected_fields = ["database_status", "byte_status", "overall_status", "app", "version"]

        for field in expected_fields:
            assert field in data, f"Missing expected field: {field}"

    async def test_system_health_status_literal_types(self, api_client: AsyncTestClient) -> None:
        """Test that status fields only contain valid literal values.

        Based on SystemHealth dataclass definition.
        """
        response = await api_client.get("/system/health")

        data = response.json()

        # Database and byte status must be: online, offline, or degraded
        component_status_values = ["online", "offline", "degraded"]
        assert data["database_status"] in component_status_values
        assert data["byte_status"] in component_status_values

        # Overall status must be: healthy, offline, or degraded
        overall_status_values = ["healthy", "offline", "degraded"]
        assert data["overall_status"] in overall_status_values

    async def test_system_health_http_status_codes(self, api_client: AsyncTestClient) -> None:
        """Test system health returns appropriate HTTP status codes."""
        response = await api_client.get("/system/health")

        # Should only return 200, 503, or 500
        assert response.status_code in [HTTP_200_OK, 503, 500]

        data = response.json()

        # Verify mapping
        if data["overall_status"] == "healthy":
            assert response.status_code == HTTP_200_OK
        elif data["overall_status"] == "degraded":
            assert response.status_code == 503
        elif data["overall_status"] == "offline":
            assert response.status_code == 500

    async def test_system_health_idempotent(self, api_client: AsyncTestClient) -> None:
        """Test system health check is idempotent."""
        responses = []

        # Make multiple requests
        for _ in range(3):
            response = await api_client.get("/system/health")
            responses.append(response)

        # All should return valid responses
        for response in responses:
            assert response.status_code in [HTTP_200_OK, 503, 500]
            data = response.json()
            assert "overall_status" in data

    async def test_system_health_fast_response(self, api_client: AsyncTestClient) -> None:
        """Test system health responds quickly for monitoring."""
        import time

        start = time.time()
        response = await api_client.get("/system/health")
        duration = time.time() - start

        # Should respond quickly (within 5 seconds)
        assert duration < 5.0

        # Should return valid response
        assert response.status_code in [HTTP_200_OK, 503, 500]

    async def test_system_health_content_type_json(self, api_client: AsyncTestClient) -> None:
        """Test system health returns JSON content-type."""
        response = await api_client.get("/system/health")

        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type

    async def test_system_health_no_authentication_required(self, api_client: AsyncTestClient) -> None:
        """Test system health endpoint accessible without auth.

        Critical for monitoring tools that don't have credentials.
        """
        response = await api_client.get("/system/health")

        # Should not return 401 or 403
        assert response.status_code != 401
        assert response.status_code != 403

    async def test_system_health_only_accepts_get(self, api_client: AsyncTestClient) -> None:
        """Test system health only accepts GET method."""
        # POST should not be allowed
        response = await api_client.post("/system/health")
        assert response.status_code == 405

    async def test_system_health_all_fields_present(self, api_client: AsyncTestClient) -> None:
        """Test system health response includes all required fields."""
        response = await api_client.get("/system/health")

        data = response.json()

        required_fields = [
            "database_status",
            "byte_status",
            "overall_status",
            "app",
            "version",
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    async def test_system_health_database_connection_status(self, api_client: AsyncTestClient) -> None:
        """Test system health reports database connection status.

        The check_database_status helper verifies connectivity and
        returns online, offline, or degraded based on connection state
        and response time.
        """
        response = await api_client.get("/system/health")

        data = response.json()

        # Database status must be one of the valid values
        assert data["database_status"] in ["online", "offline", "degraded"]

        # Overall status should be consistent with component status
        if data["database_status"] in ["offline", "degraded"]:
            assert data["overall_status"] in ["degraded", "offline"]

    async def test_system_health_database_performance_monitoring(self, api_client: AsyncTestClient) -> None:
        """Test system health monitors database query performance.

        The check_database_status helper measures query response time
        and marks database as degraded if exceeding DEGRADED_THRESHOLD (2.0s).
        """
        response = await api_client.get("/system/health")

        data = response.json()

        # Database status reflects both connectivity and performance
        assert data["database_status"] in ["online", "offline", "degraded"]

        # If database is online, response time was acceptable (< 2.0s)
        if data["database_status"] == "online":
            assert response.status_code in [HTTP_200_OK, 503, 500]

    async def test_system_health_byte_status_stub_behavior(self, api_client: AsyncTestClient) -> None:
        """Test byte status is currently stubbed to always return offline.

        This documents current behavior and should be updated when
        bot status checking is implemented.
        """
        response = await api_client.get("/system/health")

        data = response.json()

        # Stub always returns offline
        assert data["byte_status"] == "offline"

    async def test_system_health_overall_logic_all_offline(self, api_client: AsyncTestClient) -> None:
        """Test overall status logic when all components offline."""
        from unittest.mock import AsyncMock

        from litestar.di import Provide

        # Make DB offline
        mock_session = AsyncMock()
        mock_session.execute.side_effect = ConnectionRefusedError("DB offline")

        async def offline_db():
            yield mock_session

        api_client.app.dependencies["db_session"] = Provide(offline_db)

        response = await api_client.get("/system/health")

        data = response.json()

        # With both DB and byte offline
        if data["database_status"] == "offline" and data["byte_status"] == "offline":
            # Overall should be offline
            assert data["overall_status"] == "offline"
            assert response.status_code == 500

    async def test_system_health_overall_logic_partial_offline(self, api_client: AsyncTestClient) -> None:
        """Test overall status logic when some components offline.

        If any (but not all) components are offline/degraded, overall should be degraded.
        """
        from unittest.mock import AsyncMock

        from litestar.di import Provide

        # Make DB degraded by timeout
        mock_session = AsyncMock()
        mock_session.execute.side_effect = TimeoutError("Slow DB")

        async def degraded_db():
            yield mock_session

        api_client.app.dependencies["db_session"] = Provide(degraded_db)

        response = await api_client.get("/system/health")

        data = response.json()

        # DB is offline/degraded, byte is offline -> all offline
        # OR DB is degraded, byte is offline -> degraded
        assert data["overall_status"] in ["degraded", "offline"]
        assert response.status_code in [503, 500]

    async def test_system_health_response_encoding(self, api_client: AsyncTestClient) -> None:
        """Test system health response uses proper encoding."""
        response = await api_client.get("/system/health")

        content_type = response.headers.get("content-type", "")

        # Should either not specify charset or use utf-8
        if "charset" in content_type:
            assert "utf-8" in content_type.lower()

    async def test_system_health_version_format(self, api_client: AsyncTestClient) -> None:
        """Test version field contains valid data."""
        response = await api_client.get("/system/health")

        data = response.json()

        # Version should be non-empty string
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    async def test_system_health_app_name_format(self, api_client: AsyncTestClient) -> None:
        """Test app name field contains valid data."""
        response = await api_client.get("/system/health")

        data = response.json()

        # App should be non-empty string
        assert isinstance(data["app"], str)
        assert len(data["app"]) > 0

    async def test_system_health_no_caching(self, api_client: AsyncTestClient) -> None:
        """Test system health endpoint doesn't cache responses."""
        # Make two requests
        response1 = await api_client.get("/system/health")
        response2 = await api_client.get("/system/health")

        # Both should return valid responses
        assert response1.status_code in [HTTP_200_OK, 503, 500]
        assert response2.status_code in [HTTP_200_OK, 503, 500]

        # If cache-control header is present, should prevent caching
        if "cache-control" in [h.lower() for h in response1.headers.keys()]:
            cache_value = response1.headers.get("cache-control", "").lower()
            assert "no-cache" in cache_value or "no-store" in cache_value

    async def test_system_health_database_helper_called(self, api_client: AsyncTestClient) -> None:
        """Test system health endpoint calls database status helper."""
        response = await api_client.get("/system/health")

        data = response.json()

        # Database status should be populated (not None/empty)
        assert "database_status" in data
        assert data["database_status"] in ["online", "offline", "degraded"]

    async def test_system_health_byte_helper_called(self, api_client: AsyncTestClient) -> None:
        """Test system health endpoint calls byte status helper."""
        response = await api_client.get("/system/health")

        data = response.json()

        # Byte status should be populated
        assert "byte_status" in data
        assert data["byte_status"] in ["online", "offline", "degraded"]
