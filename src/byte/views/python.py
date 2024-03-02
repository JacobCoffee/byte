"""Discord UI views used in Python commands."""
from __future__ import annotations

from byte.lib.log import get_logger
from byte.views.abstract_views import BaseEmbedView

__all__ = ("PEPView",)

logger = get_logger()


class PEPView(BaseEmbedView):
    """View for the Python PEP embed."""
