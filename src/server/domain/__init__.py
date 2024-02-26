"""Application Modules."""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from litestar.dto import DTOData
from litestar.pagination import OffsetPagination
from litestar.types import TypeEncodersMap

from server.domain import db, guilds, system, urls, web
from server.domain.db.models import Guild

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from litestar.types import ControllerRouterHandler

__all__ = [
    "system",
    "web",
    "db",
    "urls",
    "routes",
    "signature_namespace",
]

routes: list[ControllerRouterHandler] = [
    system.controllers.system.SystemController,
    web.controllers.web.WebController,
    guilds.controllers.GuildsController,
]
"""Routes for the application."""

signature_namespace: Mapping[str, Any] = {
    "UUID": UUID,
    "Guild": Guild,
    "OffsetPagination": OffsetPagination,
    "GuildService": guilds.services.GuildService,
    "DTOData": DTOData,
    "TypeEncodersMap": TypeEncodersMap,
}
"""Namespace for the application signature."""
