"""Discord UI views used in Astral commands."""

from __future__ import annotations

from byte.lib.log import get_logger
from byte.views.abstract_views import ButtonEmbedView

__all__ = ("RuffView",)

logger = get_logger()


class RuffView(ButtonEmbedView):
    """View for the Ruff embed."""
