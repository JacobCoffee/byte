"""System domain DTOS."""

from dataclasses import dataclass
from typing import Annotated, Literal

from litestar.dto import DataclassDTO

from byte_api.lib import dto, settings

__all__ = ["SystemHealth", "SystemHealthDTO"]


@dataclass
class SystemHealth:
    """System Health."""

    database_status: Literal["online", "offline", "degraded"]
    byte_status: Literal["online", "offline", "degraded"]
    overall_status: Literal["healthy", "offline", "degraded"]
    app: str = settings.project.NAME
    version: str = settings.project.BUILD_NUMBER


SystemHealthDTO = DataclassDTO[Annotated[SystemHealth, dto.config()]]
