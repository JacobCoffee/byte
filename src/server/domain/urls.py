"""Domain URLs."""
from __future__ import annotations

from typing import Final

# --- System

INDEX: Final = "/"
"""Index URL."""
SITE_ROOT: Final = "/{path:str}"
"""Site root URL."""
OPENAPI_SCHEMA: Final = "/api"
"""OpenAPI schema URL."""
SYSTEM_HEALTH: Final = "/health"
"""System health URL."""

# --- Bot

# --- Reports

# --- API
GUILD_CREATE: Final = f"{OPENAPI_SCHEMA}/guilds/create"
"""Create guild URL."""
GUILD_UPDATE: Final = f"{OPENAPI_SCHEMA}/guilds/update"
"""Update guild URL."""
GUILD_DETAIL: Final = f"{OPENAPI_SCHEMA}/guilds/{{guild_id}}"
"""Guild detail URL."""
GUILD_LIST: Final = f"{OPENAPI_SCHEMA}/guilds/list"
"""Guild list URL."""
