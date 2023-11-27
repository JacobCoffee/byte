"""Byte server constants."""
from __future__ import annotations

__all__ = [
    "DB_SESSION_DEPENDENCY_KEY",
    "USER_DEPENDENCY_KEY",
    "DTO_INFO_KEY",
    "DEFAULT_PAGINATION_SIZE",
    "CACHE_EXPIRATION",
]

DB_SESSION_DEPENDENCY_KEY = "db_session"
"""The name of the key used for dependency injection of the database session."""
USER_DEPENDENCY_KEY = "current_user"
"""The name of the key used for dependency injection of the database session."""
DTO_INFO_KEY = "info"
"""The name of the key used for storing DTO information."""
DEFAULT_PAGINATION_SIZE = 20
"""Default page size to use."""
CACHE_EXPIRATION: int = 60
"""Default cache key expiration in seconds."""
