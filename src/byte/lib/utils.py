"""Byte utilities."""
from __future__ import annotations

import json
import re
import subprocess
from itertools import islice
from typing import TYPE_CHECKING, TypedDict, TypeVar

import httpx
from anyio import run_process
from discord.ext import commands
from ruff.__main__ import find_ruff_bin  # type: ignore[import-untyped]

from byte.lib import settings
from byte.lib.common import pastebin

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any

    from discord.ext.commands import Context
    from discord.ext.commands._types import Check


_T = TypeVar("_T")


# TODO: find a better place
class RuffRule(TypedDict):
    name: str
    code: str
    linter: str
    summary: str
    message_formats: list[str]
    fix: str
    explanation: str
    preview: bool


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
    "format_ruff_rule",
    "query_ruff_rule",
    "run_ruff_format",
    "paste",
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

        return any(role.name == "byte-dev" for role in ctx.author.roles)  # type: ignore[reportAttributeAccessIssue]

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


async def query_all_ruff_rules() -> list[RuffRule]:
    """Query all Ruff linting rules.

    Returns:
        list[RuffRule]: All ruff rules
    """
    _ruff = find_ruff_bin()
    try:
        result = await run_process([_ruff, "rule", "--all", "--output-format", "json"])
    except subprocess.CalledProcessError as e:
        stderr = getattr(e, "stderr", b"").decode()
        msg = f"Error while querying all rules: {stderr}"
        raise ValueError(msg) from e
    else:
        return json.loads(result.stdout.decode())


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


def chunk_sequence(sequence: Iterable[_T], size: int) -> Iterable[tuple[_T, ...]]:
    """Naïve chunking of an iterable

    Args:
        sequence (Iterable[T]): Iterable to chunk
        size (int): Size of chunk

    Yields:
        Iterable[tuple[T, ...]]: An n-tuple that contains chunked data
    """
    _sequence = iter(sequence)
    while chunk := tuple(islice(_sequence, size)):
        yield chunk
