"""Discord UI views used in Python commands."""

from __future__ import annotations

from byte_bot.lib.log import get_logger
from byte_bot.views.abstract_views import ButtonEmbedView

__all__ = ("PEPView",)

logger = get_logger()


class PEPView(ButtonEmbedView):
    """View for the Python PEP embed."""
