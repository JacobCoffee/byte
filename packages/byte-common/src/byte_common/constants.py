"""Shared constants for all Byte services."""

from __future__ import annotations

__all__ = (
    "DEFAULT_GUILD_PREFIX",
    "MAX_GUILD_NAME_LENGTH",
    "MAX_PREFIX_LENGTH",
    "MAX_TAG_NAME_LENGTH",
    "MAX_USER_NAME_LENGTH",
)

# Guild constants
DEFAULT_GUILD_PREFIX = "!"
"""Default command prefix for guilds."""

MAX_GUILD_NAME_LENGTH = 100
"""Maximum length for guild names."""

MAX_PREFIX_LENGTH = 5
"""Maximum length for command prefixes."""

# Tag constants
MAX_TAG_NAME_LENGTH = 50
"""Maximum length for Stack Overflow tag names."""

# User constants
MAX_USER_NAME_LENGTH = 100
"""Maximum length for user names."""
