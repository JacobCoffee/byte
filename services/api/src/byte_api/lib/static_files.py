"""Static files configuration."""

from __future__ import annotations

from pathlib import Path

from litestar.static_files.config import StaticFilesConfig

from byte_api.lib import settings

STATIC_DIRS = [settings.project.STATIC_DIR]
if settings.project.DEBUG:
    STATIC_DIRS.append(Path(settings.BASE_DIR / "domain" / "web" / "resources"))

config = [
    StaticFilesConfig(
        directories=STATIC_DIRS,  # type: ignore[arg-type]
        path=settings.project.STATIC_URL,
        name="web",
        html_mode=True,
        opt={"exclude_from_auth": True},
    ),
]
"""
Static files configuration. See :class:`OpenAPISettings <.settings.OpenAPISettings>` and
general :mod:`Settings.py <.settings>` for configuration.
"""
