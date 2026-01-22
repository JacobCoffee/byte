"""CORS (Cross-Origin Resource Sharing) configuration.

Provides secure CORS defaults with environment-aware origin configuration.
Production requires explicit origin configuration via CORS_ALLOW_ORIGINS.
Development environments automatically include localhost origins.
"""

from __future__ import annotations

from litestar.config.cors import CORSConfig

from byte_api.lib import settings

__all__ = ["config", "get_allowed_origins"]

DEV_LOCALHOST_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
]


def get_allowed_origins() -> list[str]:
    """Build the list of allowed CORS origins based on environment.

    For development/test environments, automatically includes localhost origins.
    For production, only explicitly configured origins are allowed.

    Returns:
        List of allowed origin URLs.
    """
    configured_origins = list(settings.cors_settings.ALLOW_ORIGINS)
    environment = settings.project.ENVIRONMENT.lower()

    is_development = environment in (
        settings.project.LOCAL_ENVIRONMENT_NAME.lower(),
        settings.project.TEST_ENVIRONMENT_NAME.lower(),
        "dev",
        "development",
    )

    if is_development:
        all_origins = set(configured_origins + DEV_LOCALHOST_ORIGINS)
        return list(all_origins)

    return configured_origins


config = CORSConfig(
    allow_origins=get_allowed_origins(),
    allow_methods=settings.cors_settings.ALLOW_METHODS,
    allow_headers=settings.cors_settings.ALLOW_HEADERS,
    allow_credentials=settings.cors_settings.ALLOW_CREDENTIALS,
    expose_headers=settings.cors_settings.EXPOSE_HEADERS,
    max_age=settings.cors_settings.MAX_AGE,
)
