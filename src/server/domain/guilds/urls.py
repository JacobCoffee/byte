"""URL configuration for the guilds domain."""
from __future__ import annotations

from typing import Final

from server.domain.urls import OPENAPI_SCHEMA

# --- Guilds
GUILDS_API: Final = f"{OPENAPI_SCHEMA}/guilds"
"""Base guilds API"""
GUILD_CREATE: Final = f"{GUILDS_API}/create"
"""URL to create a new guild manually. By default, on guild join, the bot will create a new guild database entry."""
GUILD_UPDATE: Final = f"{GUILDS_API}/update"
"""URL to update guild information on the database."""
GUILD_DETAIL: Final = f"{GUILDS_API}/{{guild_id}}"
"""URL to list current guild details by guild ID."""
GUILD_LIST: Final = f"{GUILDS_API}/list"
"""URL to list all guilds. Unless the user is a Byte Dev, this will only return the guilds the user is a member of."""
