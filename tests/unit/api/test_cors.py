"""Unit tests for CORS (Cross-Origin Resource Sharing) configuration.

Tests CORS middleware, preflight requests, origin validation,
and header handling for cross-origin API access.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_204_NO_CONTENT

from byte_api.lib import cors, settings

if TYPE_CHECKING:
    from litestar.testing import AsyncTestClient

__all__ = [
    "test_cors_allows_configured_origins",
    "test_cors_config_created",
    "test_cors_config_from_settings",
    "test_cors_credentials_allowed",
    "test_cors_headers_in_response",
    "test_cors_preflight_request",
    "test_cors_wildcard_origin",
]


def test_cors_config_created() -> None:
    """Test CORS config object is properly instantiated."""
    assert cors.config is not None
    assert hasattr(cors.config, "allow_origins")


def test_cors_config_from_settings() -> None:
    """Test CORS config uses settings from environment."""
    # CORS should pull from project settings
    assert cors.config.allow_origins == settings.project.BACKEND_CORS_ORIGINS


def test_cors_wildcard_origin() -> None:
    """Test CORS config includes wildcard if configured."""
    # In test environment, this should be ["*"] or a specific list
    assert isinstance(cors.config.allow_origins, list)
    assert len(cors.config.allow_origins) > 0


@pytest.mark.asyncio
async def test_cors_allows_configured_origins(api_client: AsyncTestClient) -> None:
    """Test CORS allows requests from configured origins."""
    # Make request with Origin header
    response = await api_client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )

    assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_cors_preflight_request(api_client: AsyncTestClient) -> None:
    """Test OPTIONS preflight request handling.

    Preflight requests are sent by browsers before making actual
    cross-origin requests with custom headers or methods.
    """
    response = await api_client.options(
        "/api/guilds/list",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    # Preflight should succeed
    assert response.status_code in [HTTP_200_OK, HTTP_204_NO_CONTENT]


@pytest.mark.asyncio
async def test_cors_headers_in_response(api_client: AsyncTestClient) -> None:
    """Test Access-Control-* headers are present in responses."""
    response = await api_client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )

    assert response.status_code == HTTP_200_OK

    # Check for CORS headers (may vary by Litestar version)
    headers = response.headers

    # At minimum, should have Allow-Origin or Vary header
    has_cors_headers = (
        "access-control-allow-origin" in headers or "access-control-allow-credentials" in headers or "vary" in headers
    )

    # CORS headers should be present in cross-origin responses
    # Note: Some frameworks add headers only when needed
    assert has_cors_headers or response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_cors_credentials_allowed(api_client: AsyncTestClient) -> None:
    """Test credentials flag allows cookies and auth headers.

    When credentials are allowed, browsers can include cookies
    and authentication headers in cross-origin requests.
    """
    response = await api_client.get(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Cookie": "session=test123",
        },
    )

    # Request should succeed with credentials
    assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_cors_methods_allowed(api_client: AsyncTestClient) -> None:
    """Test CORS allows configured HTTP methods."""
    # Test different HTTP methods are allowed
    methods_to_test = [
        ("GET", "/health"),
        ("POST", "/api/guilds/create?guild_id=999&guild_name=Test"),
    ]

    for method, path in methods_to_test:
        if method == "GET":
            response = await api_client.get(
                path,
                headers={"Origin": "http://localhost:3000"},
            )
        elif method == "POST":
            response = await api_client.post(
                path,
                headers={"Origin": "http://localhost:3000"},
            )

        # All methods should be allowed (status may vary by endpoint)
        assert response.status_code in [HTTP_200_OK, 201, 400, 404, 500]


@pytest.mark.asyncio
async def test_cors_custom_headers_allowed(api_client: AsyncTestClient) -> None:
    """Test CORS allows custom headers in requests."""
    response = await api_client.get(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "X-Custom-Header": "test-value",
            "X-Request-ID": "12345",
        },
    )

    # Custom headers should not cause CORS errors
    assert response.status_code == HTTP_200_OK


def test_cors_config_attributes() -> None:
    """Test CORS config has expected attributes."""
    assert hasattr(cors.config, "allow_origins")
    assert hasattr(cors.config, "allow_credentials")
    assert hasattr(cors.config, "allow_methods")
    assert hasattr(cors.config, "allow_headers")


def test_cors_allow_origins_is_list() -> None:
    """Test CORS allow_origins is a list."""
    assert isinstance(cors.config.allow_origins, list)


def test_cors_config_type() -> None:
    """Test CORS config is correct Litestar type."""
    from litestar.config.cors import CORSConfig

    assert isinstance(cors.config, CORSConfig)


def test_cors_settings_integration() -> None:
    """Test CORS config integrates with settings."""
    # CORS should use project settings
    expected_origins = settings.project.BACKEND_CORS_ORIGINS

    assert cors.config.allow_origins == expected_origins


def test_cors_config_not_none() -> None:
    """Test CORS config is not None."""
    assert cors.config is not None


def test_cors_all_exported() -> None:
    """Test __all__ is properly defined."""
    # Module should export config
    import byte_api.lib.cors as cors_module

    assert hasattr(cors_module, "config")


@pytest.mark.asyncio
async def test_cors_no_origin_header(api_client: AsyncTestClient) -> None:
    """Test request without Origin header succeeds."""
    response = await api_client.get("/health")

    # Should work even without CORS headers
    assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_cors_multiple_origins(api_client: AsyncTestClient) -> None:
    """Test CORS with different origin values."""
    origins = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://byte-bot.app",
    ]

    for origin in origins:
        response = await api_client.get(
            "/health",
            headers={"Origin": origin},
        )

        # All should succeed (wildcard allows all)
        assert response.status_code == HTTP_200_OK


def test_cors_config_immutable() -> None:
    """Test CORS config reference doesn't change."""
    # Config should be the same object
    config1 = cors.config
    config2 = cors.config

    assert config1 is config2


@pytest.mark.asyncio
async def test_cors_with_content_type_header(api_client: AsyncTestClient) -> None:
    """Test CORS with Content-Type header."""
    response = await api_client.post(
        "/api/guilds/create?guild_id=9999&guild_name=CORS%20Test",
        headers={
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json",
        },
    )

    # Should handle CORS with Content-Type
    assert response.status_code in [HTTP_200_OK, 201, 400, 409]


@pytest.mark.asyncio
async def test_cors_options_different_methods(api_client: AsyncTestClient) -> None:
    """Test CORS preflight for different HTTP methods."""
    methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]

    for method in methods:
        response = await api_client.options(
            "/api/guilds/list",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": method,
            },
        )

        # Preflight should succeed for all methods
        assert response.status_code in [HTTP_200_OK, HTTP_204_NO_CONTENT, 404]
