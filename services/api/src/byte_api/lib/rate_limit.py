"""Rate limiting configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.middleware.rate_limit import RateLimitConfig

from byte_api.lib import settings

if TYPE_CHECKING:
    from litestar.middleware import DefineMiddleware

__all__ = ["config", "middleware"]


def _create_rate_limit_config() -> RateLimitConfig | None:
    """Create rate limit configuration based on settings.

    Returns:
        RateLimitConfig if enabled, None otherwise.
    """
    if not settings.rate_limit.ENABLED:
        return None

    return RateLimitConfig(
        rate_limit=("minute", settings.rate_limit.REQUESTS_PER_MINUTE),
        exclude=settings.rate_limit.EXCLUDE_PATHS,
        set_rate_limit_headers=settings.rate_limit.SET_HEADERS,
    )


config = _create_rate_limit_config()


def get_middleware() -> DefineMiddleware | None:
    """Get rate limit middleware if enabled.

    Returns:
        DefineMiddleware if rate limiting is enabled, None otherwise.
    """
    if config is None:
        return None
    return config.middleware


middleware = get_middleware()
