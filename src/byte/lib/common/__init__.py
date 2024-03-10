"""Common variables and functions for use throughout Byte.

.. todo:: temporary, these are not multi-guild friendly.
"""

from byte.lib.common import assets, colors, guilds, links, mention

__all__ = (
    "assets",
    "colors",
    "guilds",
    "links",
    "config_options",
    "mention",
)

config_options: list[dict[str, str]] = [
    {"label": "Server Settings", "description": "Configure overall server settings"},
    {"label": "Forum Settings", "description": "Configure help and showcase forum settings"},
    {"label": "GitHub Settings", "description": "Configure GitHub settings"},
    {"label": "StackOverflow Settings", "description": "Configure StackOverflow settings"},
    {"label": "Allowed Users", "description": "Configure allowed users"},
    {"label": "Byte", "description": "Configure meta Byte features and settings"},
]
