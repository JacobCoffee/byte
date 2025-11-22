"""Shared settings base classes."""

from __future__ import annotations

from byte_common.settings.base import BaseAppSettings
from byte_common.settings.database import DatabaseSettings

__all__ = (
    "BaseAppSettings",
    "DatabaseSettings",
)
