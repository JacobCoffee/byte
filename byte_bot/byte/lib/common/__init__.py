"""Common variables and functions for use throughout Byte.

.. todo:: temporary, these are not multi-guild friendly.
"""

from typing import Any

from byte_bot.byte.lib.common import assets, colors, guilds, links, mention

__all__ = (
    "assets",
    "colors",
    "guilds",
    "links",
    "config_options",
    "mention",
)

config_options: list[dict[str, Any]] = [
    {
        "label": "Server Settings",
        "description": "Configure overall server settings",
        "sub_settings": [
            {"label": "Prefix", "field": "prefix", "data_type": "String"},
            {"label": "Help Channel ID", "field": "help_channel_id", "data_type": "Integer"},
            {"label": "Sync Label", "field": "sync_label", "data_type": "String"},
            {"label": "Issue Linking", "field": "issue_linking", "data_type": "True/False"},
            {"label": "Comment Linking", "field": "comment_linking", "data_type": "True/False"},
            {"label": "PEP Linking", "field": "pep_linking", "data_type": "True/False"},
        ],
    },
    {
        "label": "GitHub Settings",
        "description": "Configure GitHub settings",
        "sub_settings": [
            {"label": "Discussion Sync", "field": "discussion_sync", "data_type": "True/False"},
            {"label": "GitHub Organization", "field": "github_organization", "data_type": "String"},
            {"label": "GitHub Repository", "field": "github_repository", "data_type": "String"},
        ],
    },
    {
        "label": "StackOverflow Settings",
        "description": "Configure StackOverflow settings",
        "sub_settings": [
            {"label": "Tag Name", "field": "tag_name", "data_type": "Comma-Separated String"},
        ],
    },
    {
        "label": "Allowed Users",
        "description": "Configure allowed users",
        "sub_settings": [
            {"label": "User ID", "field": "user_id", "data_type": "Integer"},
        ],
    },
    # Forum Settings: Configure help and showcase forum settings
    # Byte Settings: Configure meta-level Byte features
]
