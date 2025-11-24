"""OpenAPI Config."""

from __future__ import annotations

from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.openapi.spec import Contact

from byte_api.lib import settings
from byte_api.lib.scalar_theme import create_scalar_plugin

__all__ = ("config",)

config = OpenAPIConfig(
    title=settings.openapi.TITLE or settings.project.NAME,
    description=settings.openapi.DESCRIPTION,
    servers=settings.openapi.SERVERS,  # type: ignore[arg-type]
    external_docs=settings.openapi.EXTERNAL_DOCS,  # type: ignore[arg-type]
    version=settings.openapi.VERSION,
    contact=Contact(name=settings.openapi.CONTACT_NAME, email=settings.openapi.CONTACT_EMAIL),
    use_handler_docstrings=True,
    path=settings.openapi.PATH,
    render_plugins=[
        create_scalar_plugin(),
        SwaggerRenderPlugin(path="/swagger"),
    ],
)
"""OpenAPI config for the project.
See :class:`OpenAPISettings <.settings.OpenAPISettings>` for configuration.
"""
