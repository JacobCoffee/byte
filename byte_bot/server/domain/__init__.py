"""Application Modules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from advanced_alchemy.service import OffsetPagination
from litestar.contrib.repository.filters import FilterTypes

from byte_bot.server.domain import db, guilds, system, urls, web

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from litestar.types import ControllerRouterHandler

__all__ = [
    "db",
    "routes",
    "signature_namespace",
    "system",
    "urls",
    "web",
]

routes: list[ControllerRouterHandler] = [
    system.controllers.system.SystemController,
    web.controllers.web.WebController,
    guilds.controllers.GuildsController,
]
"""Routes for the application."""

signature_namespace: Mapping[str, Any] = {
    "FilterTypes": FilterTypes,
    "OffsetPagination": OffsetPagination,
}
"""Namespace for the application signature."""
