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

# --- Guilds
GUILDS_API: Final = f"{OPENAPI_SCHEMA}/guilds"
GUILDS_LIST: Final = f"{GUILDS_API}/list"
