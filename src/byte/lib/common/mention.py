"""Helper functions for mentioning users, roles, and channels."""

from __future__ import annotations

__all__ = (
    "mention_channel",
    "mention_custom_emoji",
    "mention_custom_emoji_animated",
    "mention_guild_navigation",
    "mention_role",
    "mention_slash_command",
    "mention_timestamp",
    "mention_user",
    "mention_user_nickname",
)


def mention_user(user_id: int) -> str:
    """Mention a user by ID.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        A formatted string that mentions the user.
    """
    return f"<@{user_id}>"


def mention_user_nickname(user_id: int) -> str:
    """Mention a user by ID with a nickname.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        A formatted string that mentions the user with a nickname.
    """
    return f"<@!{user_id}>"


def mention_channel(channel_id: int) -> str:
    """Mention a channel by ID.

    Args:
        channel_id: The unique identifier for the channel.

    Returns:
        A formatted string that mentions the channel.
    """
    return f"<#{channel_id}>"


def mention_role(role_id: int) -> str:
    """Mention a role by ID.

    Args:
        role_id: The unique identifier for the role.

    Returns:
        A formatted string that mentions the role.
    """
    return f"<@&{role_id}>"


def mention_slash_command(name: str, command_id: int) -> str:
    """Mention a slash command by name and ID.

    Args:
        name: The name of the slash command.
        command_id: The unique identifier for the slash command.

    Returns:
        A formatted string that mentions the slash command.
    """
    return f"</{name}:{command_id}>"


def mention_custom_emoji(name: str, emoji_id: int) -> str:
    """Mention a custom emoji by name and ID.

    Args:
        name: The name of the emoji.
        emoji_id: The unique identifier for the emoji.

    Returns:
        A formatted string that mentions the custom emoji.
    """
    return f"<:{name}:{emoji_id}>"


def mention_custom_emoji_animated(name: str, emoji_id: int) -> str:
    """Mention an animated custom emoji by name and ID.

    Args:
        name: The name of the animated emoji.
        emoji_id: The unique identifier for the animated emoji.

    Returns:
        A formatted string that mentions the animated custom emoji.
    """
    return f"<a:{name}:{emoji_id}>"


def mention_timestamp(timestamp: int, style: str = "") -> str:
    """Mention a timestamp, optionally with a style.

    Args:
        timestamp: The Unix timestamp to format.
        style: An optional string representing the timestamp style.
               (Default `` ``, valid styles: ``t``, ``T``, ``d``, ``D``, ``f``, ``F``, ``R``)

    Returns:
        A formatted string that represents the timestamp.
    """
    return f"<t:{timestamp}:{style}>" if style else f"<t:{timestamp}>"


def mention_guild_navigation(guild_nav_type: str, guild_element_id: int) -> str:
    """Mention a guild navigation element by type and ID.

    Args:
        guild_nav_type: The type of the guild navigation element.
        guild_element_id: The unique identifier for the element.

    Returns:
        A formatted string that mentions the guild navigation element.
    """
    return f"<{guild_element_id}:{guild_nav_type}>"
