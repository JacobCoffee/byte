"""CORS config."""

from litestar.config.cors import CORSConfig

from byte_api.lib import settings

config = CORSConfig(allow_origins=settings.project.BACKEND_CORS_ORIGINS)
"""Default CORS config."""
