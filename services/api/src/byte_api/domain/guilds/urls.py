"""Guild URLs."""

from __future__ import annotations

from typing import Final

from byte_api.domain.urls import OPENAPI_SCHEMA

# --- API

# -- General
GUILD_CREATE: Final = f"{OPENAPI_SCHEMA}/guilds/create"
"""Create guild URL."""
GUILD_LIST: Final = f"{OPENAPI_SCHEMA}/guilds/list"
"""Guild list URL."""

# -- Specific
GUILD_UPDATE: Final = f"{OPENAPI_SCHEMA}/guilds/{{guild_id:int}}/update"
"""Update guild URL."""
GUILD_DETAIL: Final = f"{OPENAPI_SCHEMA}/guilds/{{guild_id:int}}/info"
"""Guild detail URL."""
GUILD_GITHUB_DETAIL: Final = f"{OPENAPI_SCHEMA}/guilds/{{guild_id:int}}/github/info"
"""Guild GitHub detail URL."""
GUILD_SOTAGS_DETAIL: Final = f"{OPENAPI_SCHEMA}/guilds/{{guild_id:int}}/sotags/info"
"""Guild StackOverflow tags detail URL."""
GUILD_ALLOWED_USERS_DETAIL: Final = f"{OPENAPI_SCHEMA}/guilds/{{guild_id:int}}/allowed_users/info"
"""Guild allowed users detail URL."""
GUILD_FORUM_DETAIL: Final = f"{OPENAPI_SCHEMA}/guilds/{{guild_id:int}}/forum/info"
"""Guild forum detail URL."""
