"""Custom Scalar OpenAPI theme with Byte branding."""

from __future__ import annotations

from litestar.openapi.plugins import ScalarRenderPlugin

__all__ = ("create_scalar_plugin",)


def create_scalar_plugin() -> ScalarRenderPlugin:
    """Create a Scalar plugin with custom Byte branding.

    Returns:
        Configured ScalarRenderPlugin with custom CSS
    """
    return ScalarRenderPlugin(
        path="/scalar",
        css_url="/static/css/scalar-theme.css",
    )
