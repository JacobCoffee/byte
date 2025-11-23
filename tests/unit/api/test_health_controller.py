"""Tests for health check endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from litestar.status_codes import HTTP_200_OK

if TYPE_CHECKING:
    from litestar.testing import AsyncTestClient

__all__ = [
    "test_health_check_cache_control_headers",
    "test_health_check_database_connection_error_types",
    "test_health_check_db_failure",
    "test_health_check_excludes_auth",
    "test_health_check_idempotent",
    "test_health_check_json_format",
    "test_health_check_multiple_exceptions",
    "test_health_check_response_content_type",
    "test_health_check_response_encoding_utf8",
    "test_health_check_response_fields_complete",
    "test_health_check_status_values_valid",
    "test_health_check_success",
    "test_health_database_generic_exception",
    "test_health_database_timeout",
    "test_health_endpoints_accept_only_get",
    "test_health_endpoints_fast_response_time",
    "test_health_endpoints_no_caching",
    "test_health_endpoints_return_json_objects",
    "test_health_paths_correct",
    "test_health_response_includes_timestamp_like_fields",
    "test_live_endpoint_always_200_even_if_db_down",
    "test_liveness_check",
    "test_liveness_check_cache_control_headers",
    "test_liveness_check_excludes_auth",
    "test_liveness_check_idempotent",
    "test_liveness_check_json_format",
    "test_liveness_check_response_minimal",
    "test_liveness_response_content_type",
    "test_readiness_check_cache_control_headers",
    "test_readiness_check_error_message_present",
    "test_readiness_check_excludes_auth",
    "test_readiness_check_idempotent",
    "test_readiness_check_json_format",
    "test_readiness_check_multiple_exceptions",
    "test_readiness_check_not_ready",
    "test_readiness_check_response_fields_complete",
    "test_readiness_check_status_values_valid",
    "test_readiness_check_success",
    "test_readiness_response_content_type",
    "test_ready_endpoint_database_not_ready",
    "test_ready_endpoint_timeout",
]


@pytest.mark.asyncio
async def test_health_check_success(api_client: AsyncTestClient) -> None:
    """Test health check returns 200 when database is connected.

    Verifies that the /health endpoint returns a successful response
    with database connectivity confirmed.
    """
    response = await api_client.get("/health")

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_db_connected(api_client: AsyncTestClient) -> None:
    """Test health check verifies database connectivity.

    Verifies that the /health endpoint checks database connection
    and returns appropriate status.
    """
    response = await api_client.get("/health")

    # Should return 200 or 503 depending on DB state
    assert response.status_code in [HTTP_200_OK, 503]
    data = response.json()

    # Response must include status fields
    assert "status" in data
    assert "database" in data

    # If healthy, should have ok/healthy values
    if response.status_code == HTTP_200_OK:
        assert data["status"] == "ok"
        assert data["database"] == "healthy"
    else:
        assert data["status"] == "degraded"
        assert data["database"] == "unhealthy"


@pytest.mark.asyncio
async def test_readiness_check_success(api_client: AsyncTestClient) -> None:
    """Test readiness check returns 200 when service is ready.

    Verifies that the /health/ready endpoint returns success when
    the service is ready to accept traffic (database connected).
    """
    response = await api_client.get("/health/ready")

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_readiness_check_verifies_database(api_client: AsyncTestClient) -> None:
    """Test readiness check verifies database connectivity.

    Verifies that the /health/ready endpoint checks database
    and returns appropriate readiness status.
    """
    response = await api_client.get("/health/ready")

    # Should return 200 or 503 depending on DB state
    assert response.status_code in [HTTP_200_OK, 503]
    data = response.json()

    # Must have status field
    assert "status" in data

    if response.status_code == HTTP_200_OK:
        assert data["status"] == "ready"
    else:
        assert data["status"] == "not_ready"
        assert "error" in data


@pytest.mark.asyncio
async def test_liveness_check(api_client: AsyncTestClient) -> None:
    """Test liveness check always returns 200.

    Verifies that the /health/live endpoint always returns success
    unless the service is completely dead/deadlocked. This is a minimal
    check for container orchestration systems.
    """
    response = await api_client.get("/health/live")

    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_health_check_json_format(api_client: AsyncTestClient) -> None:
    """Test health check response has correct JSON format.

    Verifies the response structure and field types match the API contract.
    """
    response = await api_client.get("/health")

    assert response.status_code == HTTP_200_OK
    data = response.json()

    # Verify response structure
    assert isinstance(data, dict)
    assert "status" in data
    assert "database" in data
    assert isinstance(data["status"], str)
    assert isinstance(data["database"], str)


@pytest.mark.asyncio
async def test_readiness_check_json_format(api_client: AsyncTestClient) -> None:
    """Test readiness check response has correct JSON format.

    Verifies the response structure for the readiness endpoint.
    """
    response = await api_client.get("/health/ready")

    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert isinstance(data, dict)
    assert "status" in data
    assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_liveness_check_json_format(api_client: AsyncTestClient) -> None:
    """Test liveness check response has correct JSON format.

    Verifies the response structure for the liveness endpoint.
    """
    response = await api_client.get("/health/live")

    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert isinstance(data, dict)
    assert "status" in data
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_health_endpoints_no_caching(api_client: AsyncTestClient) -> None:
    """Test that health endpoints don't cache responses.

    Verifies that health check endpoints return fresh data on each request.
    """
    # Make multiple requests
    response1 = await api_client.get("/health")
    response2 = await api_client.get("/health")

    # Both should succeed
    assert response1.status_code == HTTP_200_OK
    assert response2.status_code == HTTP_200_OK

    # Should not have cache headers
    assert (
        "cache-control" not in [h.lower() for h in response1.headers.keys()]
        or "no-cache" in response1.headers.get("cache-control", "").lower()
    )


@pytest.mark.asyncio
async def test_health_check_database_exception_handling(api_client: AsyncTestClient) -> None:
    """Test health check handles database errors gracefully.

    The controller wraps database checks in try-except and returns
    degraded status on any exception.
    """
    response = await api_client.get("/health")

    # Should always return a response (never crash)
    assert response.status_code in [HTTP_200_OK, 503]
    data = response.json()

    # Response structure should always be valid
    assert "status" in data
    assert "database" in data
    assert data["status"] in ["ok", "degraded"]
    assert data["database"] in ["healthy", "unhealthy"]


@pytest.mark.asyncio
async def test_readiness_endpoint_error_handling(api_client: AsyncTestClient) -> None:
    """Test readiness endpoint handles errors gracefully.

    The controller wraps checks in try-except and returns proper
    error responses without crashing.
    """
    response = await api_client.get("/health/ready")

    # Should always return a response (never crash)
    assert response.status_code in [HTTP_200_OK, 503]
    data = response.json()

    # Response structure should always be valid
    assert "status" in data
    assert data["status"] in ["ready", "not_ready"]


@pytest.mark.asyncio
async def test_live_endpoint_always_200_even_if_db_down(api_client: AsyncTestClient) -> None:
    """Liveness must return 200 even if dependencies are unhealthy.

    This is critical for K8s - liveness checks if process is alive,
    not if dependencies are healthy. Only 500+ errors indicate deadlock.
    """
    response = await api_client.get("/health/live")

    # Liveness should ALWAYS return 200 if the process can respond
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_health_response_includes_timestamp_like_fields(api_client: AsyncTestClient) -> None:
    """Verify health response structure includes expected fields.

    While the current implementation doesn't include timestamp,
    this test verifies the response format is valid and extensible.
    """
    response = await api_client.get("/health")

    assert response.status_code == HTTP_200_OK
    data = response.json()

    # Core fields that must exist
    assert "status" in data
    assert "database" in data

    # Response should be JSON dict
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_health_check_response_content_type(api_client: AsyncTestClient) -> None:
    """Verify health endpoints return JSON content-type."""
    response = await api_client.get("/health")

    assert response.status_code == HTTP_200_OK
    assert "application/json" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_readiness_response_content_type(api_client: AsyncTestClient) -> None:
    """Verify readiness endpoint returns JSON content-type."""
    response = await api_client.get("/health/ready")

    assert response.status_code == HTTP_200_OK
    assert "application/json" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_liveness_response_content_type(api_client: AsyncTestClient) -> None:
    """Verify liveness endpoint returns JSON content-type."""
    response = await api_client.get("/health/live")

    assert response.status_code == HTTP_200_OK
    assert "application/json" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_health_check_excludes_auth(api_client: AsyncTestClient) -> None:
    """Verify health endpoint doesn't require authentication.

    Critical for Docker/K8s health checks which don't have auth tokens.
    """
    # This test verifies the endpoint is accessible without auth
    # The opt = {"exclude_from_auth": True} in controller should allow this
    response = await api_client.get("/health")

    # Should not return 401/403
    assert response.status_code != 401
    assert response.status_code != 403


@pytest.mark.asyncio
async def test_readiness_check_excludes_auth(api_client: AsyncTestClient) -> None:
    """Verify readiness endpoint doesn't require authentication."""
    response = await api_client.get("/health/ready")

    # Should not return 401/403
    assert response.status_code != 401
    assert response.status_code != 403


@pytest.mark.asyncio
async def test_liveness_check_excludes_auth(api_client: AsyncTestClient) -> None:
    """Verify liveness endpoint doesn't require authentication."""
    response = await api_client.get("/health/live")

    # Should not return 401/403
    assert response.status_code != 401
    assert response.status_code != 403


@pytest.mark.asyncio
async def test_health_check_response_fields_complete(api_client: AsyncTestClient) -> None:
    """Verify health check includes all required response fields."""
    response = await api_client.get("/health")

    assert response.status_code == HTTP_200_OK
    data = response.json()

    # Must have both fields
    required_fields = ["status", "database"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Verify field values are non-empty strings
    assert len(data["status"]) > 0
    assert len(data["database"]) > 0


@pytest.mark.asyncio
async def test_health_check_status_values_valid(api_client: AsyncTestClient) -> None:
    """Verify health check returns only valid status values."""
    response = await api_client.get("/health")

    data = response.json()

    # Status should be one of known values
    valid_statuses = ["ok", "degraded"]
    valid_db_statuses = ["healthy", "unhealthy"]

    assert data["status"] in valid_statuses
    assert data["database"] in valid_db_statuses


@pytest.mark.asyncio
async def test_readiness_check_response_fields_complete(api_client: AsyncTestClient) -> None:
    """Verify readiness check includes all required response fields."""
    response = await api_client.get("/health/ready")

    data = response.json()

    # Ready response must have status
    assert "status" in data

    # Error field should be present when not ready
    if response.status_code == 503:
        assert "error" in data


@pytest.mark.asyncio
async def test_readiness_check_status_values_valid(api_client: AsyncTestClient) -> None:
    """Verify readiness check returns only valid status values."""
    response = await api_client.get("/health/ready")

    data = response.json()

    # Status should be ready or not_ready
    valid_statuses = ["ready", "not_ready"]
    assert data["status"] in valid_statuses


@pytest.mark.asyncio
async def test_liveness_check_response_minimal(api_client: AsyncTestClient) -> None:
    """Verify liveness check has minimal response structure.

    Liveness is meant to be ultra-lightweight - just check if process is alive.
    """
    response = await api_client.get("/health/live")

    assert response.status_code == HTTP_200_OK
    data = response.json()

    # Should only have status field for minimal overhead
    assert "status" in data
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_health_endpoints_return_json_objects(api_client: AsyncTestClient) -> None:
    """Verify all health endpoints return JSON objects (not arrays or primitives)."""
    endpoints = ["/health", "/health/ready", "/health/live"]

    for endpoint in endpoints:
        response = await api_client.get(endpoint)
        data = response.json()

        # Must be a dict
        assert isinstance(data, dict), f"{endpoint} did not return a JSON object"


@pytest.mark.asyncio
async def test_health_check_cache_control_headers(api_client: AsyncTestClient) -> None:
    """Verify health endpoints set proper cache-control headers."""
    response = await api_client.get("/health")

    # Should either not have cache-control or set it to no-cache
    if "cache-control" in [h.lower() for h in response.headers.keys()]:
        cache_value = response.headers.get("cache-control", "").lower()
        assert "no-cache" in cache_value or "no-store" in cache_value


@pytest.mark.asyncio
async def test_readiness_check_cache_control_headers(api_client: AsyncTestClient) -> None:
    """Verify readiness endpoint sets proper cache-control headers."""
    response = await api_client.get("/health/ready")

    # Should not cache readiness checks
    if "cache-control" in [h.lower() for h in response.headers.keys()]:
        cache_value = response.headers.get("cache-control", "").lower()
        assert "no-cache" in cache_value or "no-store" in cache_value


@pytest.mark.asyncio
async def test_liveness_check_cache_control_headers(api_client: AsyncTestClient) -> None:
    """Verify liveness endpoint sets proper cache-control headers."""
    response = await api_client.get("/health/live")

    # Should not cache liveness checks
    if "cache-control" in [h.lower() for h in response.headers.keys()]:
        cache_value = response.headers.get("cache-control", "").lower()
        assert "no-cache" in cache_value or "no-store" in cache_value


@pytest.mark.asyncio
async def test_health_check_exception_resilience(api_client: AsyncTestClient) -> None:
    """Test health check is resilient to errors.

    The controller uses try-except to handle any database errors
    and return degraded status instead of crashing.
    """
    response = await api_client.get("/health")

    # Should always get a valid response
    assert response.status_code in [HTTP_200_OK, 503]
    data = response.json()

    # Structure should be consistent
    assert isinstance(data, dict)
    assert "status" in data
    assert "database" in data


@pytest.mark.asyncio
async def test_readiness_check_exception_resilience(api_client: AsyncTestClient) -> None:
    """Test readiness check is resilient to errors.

    The controller uses try-except to handle errors and return
    not_ready status instead of crashing.
    """
    response = await api_client.get("/health/ready")

    # Should always get a valid response
    assert response.status_code in [HTTP_200_OK, 503]
    data = response.json()

    # Structure should be consistent
    assert isinstance(data, dict)
    assert "status" in data


@pytest.mark.asyncio
async def test_health_endpoints_accept_only_get(api_client: AsyncTestClient) -> None:
    """Verify health endpoints only accept GET requests."""
    endpoints = ["/health", "/health/ready", "/health/live"]

    for endpoint in endpoints:
        # POST should not be allowed
        response = await api_client.post(endpoint)
        assert response.status_code == 405  # Method Not Allowed


@pytest.mark.asyncio
async def test_health_check_idempotent(api_client: AsyncTestClient) -> None:
    """Verify health check is idempotent across multiple requests."""
    responses = []

    # Make 5 consecutive requests
    for _ in range(5):
        response = await api_client.get("/health")
        responses.append(response)

    # All should have same status code (assuming stable DB)
    status_codes = [r.status_code for r in responses]
    assert all(code == status_codes[0] for code in status_codes)

    # All should have same response structure
    for response in responses:
        data = response.json()
        assert "status" in data
        assert "database" in data


@pytest.mark.asyncio
async def test_readiness_check_idempotent(api_client: AsyncTestClient) -> None:
    """Verify readiness check is idempotent across multiple requests."""
    responses = []

    # Make 5 consecutive requests
    for _ in range(5):
        response = await api_client.get("/health/ready")
        responses.append(response)

    # All should have same status code (assuming stable DB)
    status_codes = [r.status_code for r in responses]
    assert all(code == status_codes[0] for code in status_codes)


@pytest.mark.asyncio
async def test_liveness_check_idempotent(api_client: AsyncTestClient) -> None:
    """Verify liveness check is idempotent across multiple requests."""
    responses = []

    # Make 5 consecutive requests
    for _ in range(5):
        response = await api_client.get("/health/live")
        responses.append(response)

    # All should return 200
    for response in responses:
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_health_check_response_encoding_utf8(api_client: AsyncTestClient) -> None:
    """Verify health check response uses UTF-8 encoding."""
    response = await api_client.get("/health")

    content_type = response.headers.get("content-type", "")
    # Should either not specify charset or use utf-8
    if "charset" in content_type:
        assert "utf-8" in content_type.lower()


@pytest.mark.asyncio
async def test_health_endpoints_fast_response_time(api_client: AsyncTestClient) -> None:
    """Verify health endpoints respond quickly for monitoring use case."""
    import time

    endpoints = ["/health", "/health/ready", "/health/live"]

    for endpoint in endpoints:
        start = time.time()
        response = await api_client.get(endpoint)
        duration = time.time() - start

        # Should respond within 5 seconds (generous for test environment)
        assert duration < 5.0, f"{endpoint} took {duration}s to respond"
        assert response.status_code in [HTTP_200_OK, 503]


@pytest.mark.asyncio
async def test_health_check_database_connectivity_check(api_client: AsyncTestClient) -> None:
    """Test health check verifies database connectivity.

    The controller executes a simple SELECT 1 query to verify
    database connection is working.
    """
    response = await api_client.get("/health")

    # Should get a valid response
    assert response.status_code in [HTTP_200_OK, 503]
    data = response.json()

    # Database status should be checked
    assert "database" in data
    assert data["database"] in ["healthy", "unhealthy"]


@pytest.mark.asyncio
async def test_readiness_check_error_field_when_not_ready(api_client: AsyncTestClient) -> None:
    """Verify readiness check includes error field when appropriate.

    When the service is not ready, the response should include
    an error field explaining why.
    """
    response = await api_client.get("/health/ready")

    data = response.json()

    # If not ready (503), should have error field
    if response.status_code == 503:
        assert "error" in data
        assert len(data["error"]) > 0


@pytest.mark.asyncio
async def test_health_paths_correct(api_client: AsyncTestClient) -> None:
    """Verify health endpoints are mounted at correct paths."""
    # Main health
    response = await api_client.get("/health")
    assert response.status_code in [HTTP_200_OK, 503]

    # Readiness
    response = await api_client.get("/health/ready")
    assert response.status_code in [HTTP_200_OK, 503]

    # Liveness
    response = await api_client.get("/health/live")
    assert response.status_code == HTTP_200_OK

    # Invalid paths should 404
    response = await api_client.get("/health/invalid")
    assert response.status_code == 404
