"""Helper functions for use within the GitHub domain."""
from __future__ import annotations

from githubkit import AppInstallationAuthStrategy, GitHub  # type: ignore[reportMissingImports]

from src.server.lib import settings

__all__ = ("github_client",)

github_client = GitHub(
    AppInstallationAuthStrategy(
        app_id=settings.github.APP_ID,
        private_key=settings.github.APP_PRIVATE_KEY,
        installation_id=44969171,
        client_id=settings.github.APP_CLIENT_ID,
        client_secret=settings.github.APP_CLIENT_SECRET,
    )
)
