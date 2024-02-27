"""Byte utilities."""
from __future__ import annotations

import json
import re
import subprocess
from typing import TYPE_CHECKING, Any

import httpx
from discord.ext import commands
from ruff.__main__ import find_ruff_bin  # type: ignore[import-untyped]

from byte.lib import settings
from byte.lib.common import pastebin

if TYPE_CHECKING:
    from typing import Any

    from discord.ext.commands import Context
    from discord.ext.commands._types import Check

__all__ = (
    "is_byte_dev",
    "linker",
    "mention_user",
    "mention_user_nickname",
    "mention_channel",
    "mention_role",
    "mention_slash_command",
    "mention_custom_emoji",
    "mention_custom_emoji_animated",
    "mention_timestamp",
    "mention_guild_navigation",
)


def is_byte_dev() -> Check[Any]:
    """Check if the user is a Byte developer.

    Returns:
        A check function.
    """

    async def predicate(ctx: Context) -> bool:
        """Check if the user is a Byte Dev or Owner.

        Args:
            ctx: Context object.

        Returns:
            True if the user is a Byte Dev or Owner, False otherwise.
        """
        if await ctx.bot.is_owner(ctx.author) or ctx.author.id == settings.discord.DEV_USER_ID:
            return True

        return any(role.name == "byte-dev" for role in ctx.author.roles)

    return commands.check(predicate)


def linker(title: str, link: str, show_embed: bool = False) -> str:
    """Create a Markdown link, optionally with an embed.

    Args:
        title: The title of the link.
        link: The URL of the link.
        show_embed: Whether to show the embed or not.

    Returns:
        A Markdown link.
    """
    return f"[{title}]({link})" if show_embed else f"[{title}](<{link}>)"


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


def format_ruff_rule(rule_data: dict) -> dict[str, str | Any]:
    """Format ruff rule data for embed-friendly output and append rule link.

    Args:
        rule_data: The ruff rule data.

    Returns:
        The formatted rule data as a string.
    """
    explanation_formatted = re.sub(r"## (.+)", r"**\1**", rule_data["explanation"])
    rule_name = rule_data["code"]
    rule_link = f"https://docs.astral.sh/ruff/rules/#{rule_name}"

    return {
        "name": rule_data.get("name", "No name available"),
        "summary": rule_data.get("summary", "No summary available"),
        "explanation": explanation_formatted,
        "fix": rule_data.get("fix", "No fix available"),
        "rule_link": rule_link,
    }


def query_ruff_rule(rule: str) -> dict[str, Any]:
    """Query a Ruff linting rule.

    Args:
        rule: The rule to query.

    Returns:
        dict[str, Any]: The resulting rule, if found or an error dict.
    """
    _ruff = find_ruff_bin()

    try:
        result = subprocess.run(
            [_ruff, "rule", "--output-format", "json", rule],  # noqa: S603
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        if "invalid value" in e.stderr:
            return {"error": f"Rule '{rule}' not found."}
        msg = f"Error querying rule {rule}: {e.stderr}"
        raise ValueError(msg) from e

    rule_data = json.loads(result.stdout)
    return format_ruff_rule(rule_data)


def run_ruff_format(code: str) -> str:
    """Formats code using Ruff.

    Args:
        code: The code to format.

    Returns:
        str: The formatted code.
    """
    result = subprocess.run(
        ["ruff", "format", "-"],  # noqa: S603, S607
        input=code,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else code


async def paste(code: str) -> str:
    """Uploads the given code to paste.pythondiscord.com.

    Args:
        code: The formatted code to upload.

    Returns:
        str: The URL of the uploaded paste.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{pastebin}/api/v1/paste",
            json={
                "expiry": "1day",
                "files": [{"name": "byte-bot_formatted_code.py", "lexer": "python", "content": code}],
            },
        )
        response_data = response.json()
        paste_link = response_data.get("link")
        return paste_link or "Failed to upload formatted code."
