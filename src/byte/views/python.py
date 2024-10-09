"""Discord UI views used in Python commands."""
from __future__ import annotations

from src.byte.lib.log import get_logger
from src.byte.views.abstract_views import BaseEmbedView

__all__ = ("PEPView",)

logger = get_logger()


class PEPView(BaseEmbedView):
    """View for the Python PEP embed."""
