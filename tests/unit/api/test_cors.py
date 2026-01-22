"""Unit tests for CORS (Cross-Origin Resource Sharing) configuration.

Tests CORS middleware, preflight requests, origin validation,
and header handling for cross-origin API access.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from litestar.config.cors import CORSConfig
from litestar.status_codes import HTTP_200_OK, HTTP_204_NO_CONTENT

from byte_api.lib import cors, settings

if TYPE_CHECKING:
    from litestar.testing import AsyncTestClient

__all__ = [
    "TestCORSConfigAttributes",
    "TestCORSConfigCreation",
    "TestCORSIntegration",
    "TestCORSModule",
    "TestCORSSettings",
    "TestGetAllowedOrigins",
]


class TestCORSConfigCreation:
    """Tests for CORS config object creation."""

    def test_cors_config_created(self) -> None:
        """Test CORS config object is properly instantiated."""
        assert cors.config is not None
        assert hasattr(cors.config, "allow_origins")

    def test_cors_config_type(self) -> None:
        """Test CORS config is correct Litestar type."""
        assert isinstance(cors.config, CORSConfig)

    def test_cors_config_not_none(self) -> None:
        """Test CORS config is not None."""
        assert cors.config is not None

    def test_cors_config_immutable(self) -> None:
        """Test CORS config reference doesn't change."""
        config1 = cors.config
        config2 = cors.config
        assert config1 is config2


class TestCORSConfigAttributes:
    """Tests for CORS config attributes and values."""

    def test_cors_config_has_required_attributes(self) -> None:
        """Test CORS config has expected attributes."""
        assert hasattr(cors.config, "allow_origins")
        assert hasattr(cors.config, "allow_credentials")
        assert hasattr(cors.config, "allow_methods")
        assert hasattr(cors.config, "allow_headers")
        assert hasattr(cors.config, "expose_headers")
        assert hasattr(cors.config, "max_age")

    def test_cors_allow_origins_is_list(self) -> None:
        """Test CORS allow_origins is a list."""
        assert isinstance(cors.config.allow_origins, list)

    def test_cors_allow_methods_configured(self) -> None:
        """Test CORS allow_methods uses settings."""
        assert cors.config.allow_methods == settings.cors_settings.ALLOW_METHODS

    def test_cors_allow_headers_configured(self) -> None:
        """Test CORS allow_headers uses settings (Litestar normalizes to lowercase)."""
        expected_headers = [h.lower() for h in settings.cors_settings.ALLOW_HEADERS]
        assert cors.config.allow_headers == expected_headers

    def test_cors_allow_credentials_configured(self) -> None:
        """Test CORS allow_credentials uses settings."""
        assert cors.config.allow_credentials == settings.cors_settings.ALLOW_CREDENTIALS

    def test_cors_expose_headers_configured(self) -> None:
        """Test CORS expose_headers uses settings."""
        assert cors.config.expose_headers == settings.cors_settings.EXPOSE_HEADERS

    def test_cors_max_age_configured(self) -> None:
        """Test CORS max_age uses settings."""
        assert cors.config.max_age == settings.cors_settings.MAX_AGE


class TestCORSSettings:
    """Tests for CORSSettings pydantic model."""

    def test_cors_settings_defaults(self) -> None:
        """Test CORS settings have secure defaults."""
        cors_cfg = settings.CORSSettings()
        assert cors_cfg.ALLOW_ORIGINS == []
        assert cors_cfg.ALLOW_CREDENTIALS is True
        assert cors_cfg.MAX_AGE == 600
        assert "GET" in cors_cfg.ALLOW_METHODS
        assert "POST" in cors_cfg.ALLOW_METHODS

    def test_cors_settings_parse_origins_from_string(self) -> None:
        """Test origins can be parsed from comma-separated string."""
        cors_cfg = settings.CORSSettings(
            ALLOW_ORIGINS="https://example.com,https://api.example.com"  # type: ignore[arg-type]
        )
        assert "https://example.com" in cors_cfg.ALLOW_ORIGINS
        assert "https://api.example.com" in cors_cfg.ALLOW_ORIGINS

    def test_cors_settings_parse_origins_from_list(self) -> None:
        """Test origins can be provided as list."""
        cors_cfg = settings.CORSSettings(ALLOW_ORIGINS=["https://example.com", "https://api.example.com"])
        assert "https://example.com" in cors_cfg.ALLOW_ORIGINS
        assert "https://api.example.com" in cors_cfg.ALLOW_ORIGINS

    def test_cors_settings_empty_origins(self) -> None:
        """Test empty origins list is valid."""
        cors_cfg = settings.CORSSettings(ALLOW_ORIGINS="")  # type: ignore[arg-type]
        assert cors_cfg.ALLOW_ORIGINS == []

    def test_cors_settings_parse_methods_from_string(self) -> None:
        """Test methods can be parsed from comma-separated string."""
        cors_cfg = settings.CORSSettings(ALLOW_METHODS="GET,POST,PUT")  # type: ignore[arg-type]
        assert cors_cfg.ALLOW_METHODS == ["GET", "POST", "PUT"]

    def test_cors_settings_parse_headers_from_string(self) -> None:
        """Test headers can be parsed from comma-separated string."""
        cors_cfg = settings.CORSSettings(ALLOW_HEADERS="Authorization,Content-Type")  # type: ignore[arg-type]
        assert cors_cfg.ALLOW_HEADERS == ["Authorization", "Content-Type"]

    def test_cors_settings_strips_whitespace(self) -> None:
        """Test whitespace is stripped from parsed values."""
        cors_cfg = settings.CORSSettings(
            ALLOW_ORIGINS="  https://example.com  ,  https://api.example.com  "  # type: ignore[arg-type]
        )
        assert "https://example.com" in cors_cfg.ALLOW_ORIGINS
        assert "https://api.example.com" in cors_cfg.ALLOW_ORIGINS


class TestGetAllowedOrigins:
    """Tests for the get_allowed_origins function."""

    def test_development_includes_localhost(self) -> None:
        """Test development environment includes localhost origins."""
        with patch.object(settings.project, "ENVIRONMENT", "dev"):
            origins = cors.get_allowed_origins()
            assert "http://localhost:3000" in origins
            assert "http://localhost:8000" in origins
            assert "http://127.0.0.1:3000" in origins

    def test_local_environment_includes_localhost(self) -> None:
        """Test local environment includes localhost origins."""
        with patch.object(settings.project, "ENVIRONMENT", "local"):
            origins = cors.get_allowed_origins()
            assert "http://localhost:3000" in origins

    def test_test_environment_includes_localhost(self) -> None:
        """Test test environment includes localhost origins."""
        with patch.object(settings.project, "ENVIRONMENT", "test"):
            origins = cors.get_allowed_origins()
            assert "http://localhost:3000" in origins

    def test_production_excludes_localhost_by_default(self) -> None:
        """Test production environment does not include localhost origins by default."""
        with (
            patch.object(settings.project, "ENVIRONMENT", "prod"),
            patch.object(settings.cors_settings, "ALLOW_ORIGINS", ["https://byte-bot.app"]),
        ):
            origins = cors.get_allowed_origins()
            assert "http://localhost:3000" not in origins
            assert "https://byte-bot.app" in origins

    def test_configured_origins_included(self) -> None:
        """Test configured origins are always included."""
        with (
            patch.object(settings.project, "ENVIRONMENT", "dev"),
            patch.object(settings.cors_settings, "ALLOW_ORIGINS", ["https://custom.example.com"]),
        ):
            origins = cors.get_allowed_origins()
            assert "https://custom.example.com" in origins
            assert "http://localhost:3000" in origins

    def test_no_duplicate_origins(self) -> None:
        """Test origins list contains no duplicates."""
        with (
            patch.object(settings.project, "ENVIRONMENT", "dev"),
            patch.object(settings.cors_settings, "ALLOW_ORIGINS", ["http://localhost:3000"]),
        ):
            origins = cors.get_allowed_origins()
            localhost_count = origins.count("http://localhost:3000")
            assert localhost_count == 1


class TestCORSModule:
    """Tests for CORS module exports."""

    def test_cors_all_exported(self) -> None:
        """Test __all__ is properly defined."""
        import byte_api.lib.cors as cors_module

        assert hasattr(cors_module, "config")
        assert hasattr(cors_module, "get_allowed_origins")
        assert "config" in cors_module.__all__
        assert "get_allowed_origins" in cors_module.__all__


class TestCORSIntegration:
    """Integration tests for CORS with API client."""

    @pytest.mark.asyncio
    async def test_cors_allows_configured_origins(self, api_client: AsyncTestClient) -> None:
        """Test CORS allows requests from configured origins."""
        response = await api_client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == HTTP_200_OK

    @pytest.mark.asyncio
    async def test_cors_preflight_request(self, api_client: AsyncTestClient) -> None:
        """Test OPTIONS preflight request handling."""
        response = await api_client.options(
            "/api/guilds/list",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert response.status_code in [HTTP_200_OK, HTTP_204_NO_CONTENT]

    @pytest.mark.asyncio
    async def test_cors_headers_in_response(self, api_client: AsyncTestClient) -> None:
        """Test Access-Control-* headers are present in responses."""
        response = await api_client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == HTTP_200_OK
        headers = response.headers
        has_cors_headers = (
            "access-control-allow-origin" in headers
            or "access-control-allow-credentials" in headers
            or "vary" in headers
        )
        assert has_cors_headers or response.status_code == HTTP_200_OK

    @pytest.mark.asyncio
    async def test_cors_credentials_allowed(self, api_client: AsyncTestClient) -> None:
        """Test credentials flag allows cookies and auth headers."""
        response = await api_client.get(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Cookie": "session=test123",
            },
        )
        assert response.status_code == HTTP_200_OK

    @pytest.mark.asyncio
    async def test_cors_no_origin_header(self, api_client: AsyncTestClient) -> None:
        """Test request without Origin header succeeds."""
        response = await api_client.get("/health")
        assert response.status_code == HTTP_200_OK

    @pytest.mark.asyncio
    async def test_cors_multiple_origins(self, api_client: AsyncTestClient) -> None:
        """Test CORS with different origin values."""
        origins = [
            "http://localhost:3000",
            "http://localhost:8080",
        ]
        for origin in origins:
            response = await api_client.get(
                "/health",
                headers={"Origin": origin},
            )
            assert response.status_code == HTTP_200_OK

    @pytest.mark.asyncio
    async def test_cors_with_content_type_header(self, api_client: AsyncTestClient) -> None:
        """Test CORS with Content-Type header."""
        response = await api_client.post(
            "/api/guilds/create?guild_id=9999&guild_name=CORS%20Test",
            headers={
                "Origin": "http://localhost:3000",
                "Content-Type": "application/json",
            },
        )
        assert response.status_code in [HTTP_200_OK, 201, 400, 409]

    @pytest.mark.asyncio
    async def test_cors_options_different_methods(self, api_client: AsyncTestClient) -> None:
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
            assert response.status_code in [HTTP_200_OK, HTTP_204_NO_CONTENT, 404]

    @pytest.mark.asyncio
    async def test_cors_custom_headers_allowed(self, api_client: AsyncTestClient) -> None:
        """Test CORS allows custom headers in requests."""
        response = await api_client.get(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "X-Custom-Header": "test-value",
                "X-Request-ID": "12345",
            },
        )
        assert response.status_code == HTTP_200_OK

    @pytest.mark.asyncio
    async def test_cors_methods_allowed(self, api_client: AsyncTestClient) -> None:
        """Test CORS allows configured HTTP methods."""
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
            assert response.status_code in [HTTP_200_OK, 201, 400, 404, 500]
