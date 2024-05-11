"""Guild URLs."""
from __future__ import annotations

from typing import Final

from server.domain.urls import OPENAPI_SCHEMA

# --- API

# -- General
GUILD_CREATE: Final = f"{OPENAPI_SCHEMA}/guilds/create"
"""Create guild URL."""
GUILD_LIST: Final = f"{OPENAPI_SCHEMA}/guilds/list"
"""Guild list URL."""

# -- Specific
GUILD_UPDATE: Final = f"{OPENAPI_SCHEMA}/guilds/{{guild_id}}/update"
"""Update guild URL."""
GUILD_DETAIL: Final = f"{OPENAPI_SCHEMA}/guilds/{{guild_id}}/info"
"""Guild detail URL."""
