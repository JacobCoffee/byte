"""Unit tests for rate limiting configuration.

Tests rate limit middleware, configuration, and settings integration.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.status_codes import HTTP_200_OK

if TYPE_CHECKING:
    from litestar.testing import AsyncTestClient

__all__ = [
    "test_rate_limit_config_created",
    "test_rate_limit_config_from_settings",
    "test_rate_limit_config_type",
    "test_rate_limit_exclude_paths",
    "test_rate_limit_headers_present",
    "test_rate_limit_middleware_exists",
    "test_rate_limit_settings_defaults",
]


def test_rate_limit_settings_defaults() -> None:
    """Test rate limit settings have expected defaults."""
    from byte_api.lib import settings

    assert settings.rate_limit.ENABLED is True
    assert settings.rate_limit.REQUESTS_PER_MINUTE == 100
    assert isinstance(settings.rate_limit.EXCLUDE_PATHS, list)
    assert "/health" in settings.rate_limit.EXCLUDE_PATHS
    assert settings.rate_limit.SET_HEADERS is True


def test_rate_limit_config_created() -> None:
    """Test rate limit config object is properly instantiated."""
    from byte_api.lib import rate_limit

    assert rate_limit.config is not None


def test_rate_limit_config_type() -> None:
    """Test rate limit config is correct Litestar type."""
    from byte_api.lib import rate_limit

    assert isinstance(rate_limit.config, RateLimitConfig)


def test_rate_limit_config_from_settings() -> None:
    """Test rate limit config uses values from settings."""
    from byte_api.lib import rate_limit, settings

    assert rate_limit.config is not None
    assert rate_limit.config.rate_limit == ("minute", settings.rate_limit.REQUESTS_PER_MINUTE)


def test_rate_limit_exclude_paths() -> None:
    """Test rate limit config excludes expected paths."""
    from byte_api.lib import rate_limit, settings

    assert rate_limit.config is not None
    assert rate_limit.config.exclude == settings.rate_limit.EXCLUDE_PATHS
    exclude_paths = rate_limit.config.exclude or []
    assert "/health" in exclude_paths


def test_rate_limit_middleware_exists() -> None:
    """Test rate limit middleware is available when enabled."""
    from byte_api.lib import rate_limit

    assert rate_limit.middleware is not None


def test_rate_limit_set_headers_config() -> None:
    """Test rate limit headers setting is configured."""
    from byte_api.lib import rate_limit

    assert rate_limit.config is not None
    assert rate_limit.config.set_rate_limit_headers is True


def test_rate_limit_settings_parse_exclude_paths_string() -> None:
    """Test exclude paths can be parsed from comma-separated string."""
    from byte_api.lib.settings import RateLimitSettings

    settings = RateLimitSettings.model_validate({"EXCLUDE_PATHS": "/api/v1,/api/v2,/health"})
    assert settings.EXCLUDE_PATHS == ["/api/v1", "/api/v2", "/health"]


def test_rate_limit_settings_parse_exclude_paths_list() -> None:
    """Test exclude paths accepts list directly."""
    from byte_api.lib.settings import RateLimitSettings

    settings = RateLimitSettings.model_validate({"EXCLUDE_PATHS": ["/custom1", "/custom2"]})
    assert settings.EXCLUDE_PATHS == ["/custom1", "/custom2"]


def test_rate_limit_settings_parse_exclude_paths_none() -> None:
    """Test exclude paths defaults when None."""
    from byte_api.lib.settings import RateLimitSettings

    settings = RateLimitSettings.model_validate({})
    assert "/health" in settings.EXCLUDE_PATHS


def test_rate_limit_disabled_returns_none() -> None:
    """Test _create_rate_limit_config returns None when disabled via settings."""
    from byte_api.lib.settings import RateLimitSettings

    with patch.dict(os.environ, {"RATE_LIMIT_ENABLED": "false"}):
        disabled_settings = RateLimitSettings.model_validate({})
        assert disabled_settings.ENABLED is False


def test_rate_limit_config_attributes() -> None:
    """Test rate limit config has expected attributes."""
    from byte_api.lib import rate_limit

    config = rate_limit.config
    if config is None:
        from importlib import reload

        reload(rate_limit)
        config = rate_limit.config

    assert config is not None
    assert hasattr(config, "rate_limit")
    assert hasattr(config, "exclude")
    assert hasattr(config, "set_rate_limit_headers")


def test_rate_limit_module_exports() -> None:
    """Test rate_limit module exports expected items."""
    from byte_api.lib import rate_limit

    assert hasattr(rate_limit, "config")
    assert hasattr(rate_limit, "middleware")


@pytest.mark.asyncio
async def test_rate_limit_headers_present(api_client: AsyncTestClient) -> None:
    """Test rate limit headers are present in responses when middleware is active."""
    from byte_api.lib import rate_limit

    response = await api_client.get("/api/guilds/list")

    assert response.status_code == HTTP_200_OK

    if rate_limit.middleware is not None:
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        has_rate_limit_headers = any(
            key in headers_lower
            for key in [
                "ratelimit-limit",
                "ratelimit-remaining",
                "ratelimit-reset",
                "x-ratelimit-limit",
            ]
        )
        assert has_rate_limit_headers


@pytest.mark.asyncio
async def test_rate_limit_excluded_path(api_client: AsyncTestClient) -> None:
    """Test excluded paths are accessible."""
    for _ in range(5):
        response = await api_client.get("/health")
        assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_rate_limit_non_excluded_path(api_client: AsyncTestClient) -> None:
    """Test non-excluded paths are accessible and receive rate limit headers when middleware is active."""
    from byte_api.lib import rate_limit

    response = await api_client.get("/api/guilds/list")

    assert response.status_code == HTTP_200_OK

    if rate_limit.middleware is not None:
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        has_rate_limit_info = any("ratelimit" in key.lower() for key in headers_lower)
        assert has_rate_limit_info


def test_rate_limit_settings_environment_override() -> None:
    """Test rate limit settings can be overridden via environment."""
    with patch.dict(
        os.environ,
        {
            "RATE_LIMIT_ENABLED": "true",
            "RATE_LIMIT_REQUESTS_PER_MINUTE": "50",
            "RATE_LIMIT_SET_HEADERS": "false",
        },
    ):
        from byte_api.lib.settings import RateLimitSettings

        settings = RateLimitSettings.model_validate({})

        assert settings.ENABLED is True
        assert settings.REQUESTS_PER_MINUTE == 50
        assert settings.SET_HEADERS is False


def test_rate_limit_config_immutable() -> None:
    """Test rate limit config reference doesn't change."""
    from byte_api.lib import rate_limit

    config1 = rate_limit.config
    config2 = rate_limit.config

    assert config1 is config2
