"""Template config.

See TemplateSettings for configuration.
"""

from __future__ import annotations

from litestar.template.config import TemplateConfig

from server.lib import settings

config = TemplateConfig(
    directory=settings.TEMPLATES_DIR,
    engine=settings.template.ENGINE,
)
"""
Template config for project.
See :class:`TemplateSettings <.settings.TemplateSettings>` for configuration.
"""
