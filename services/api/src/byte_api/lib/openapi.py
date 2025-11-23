"""OpenAPI Config."""

from __future__ import annotations

from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.spec import Contact

from byte_api.lib import settings

__all__ = ("config",)

config = OpenAPIConfig(
    title=settings.openapi.TITLE or settings.project.NAME,
    description=settings.openapi.DESCRIPTION,
    servers=settings.openapi.SERVERS,  # type: ignore[arg-type]
    external_docs=settings.openapi.EXTERNAL_DOCS,  # type: ignore[arg-type]
    version=settings.openapi.VERSION,
    contact=Contact(name=settings.openapi.CONTACT_NAME, email=settings.openapi.CONTACT_EMAIL),
    use_handler_docstrings=True,
    root_schema_site="swagger",
    path=settings.openapi.PATH,
)
"""OpenAPI config for the project.
See :class:`OpenAPISettings <.settings.OpenAPISettings>` for configuration.
"""
