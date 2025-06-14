"""Byte utilities."""

from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
from datetime import UTC, datetime
from itertools import islice
from typing import TYPE_CHECKING, TypeVar

import httpx
from anyio import run_process
from ruff.__main__ import find_ruff_bin  # type: ignore[import-untyped]

from byte_bot.byte.lib.common.links import pastebin
from byte_bot.byte.lib.types.python import PEP, PEPStatus, PEPType

if TYPE_CHECKING:
    from collections.abc import Iterable

    from byte_bot.byte.lib.types.astral import FormattedRuffRule, RuffRule

__all__ = (
    "PEP",
    "BaseRuffRule",
    "FormattedRuffRule",
    "RuffRule",
    "chunk_sequence",
    "format_ruff_rule",
    "PEP",
    "PEPType",
    "PEPStatus",
    "PEPHistoryItem",
    "is_guild_admin",
    "is_byte_dev",
    "linker",
    "mention_channel",
    "mention_custom_emoji",
    "mention_custom_emoji_animated",
    "mention_guild_navigation",
    "mention_role",
    "mention_slash_command",
    "mention_timestamp",
    "mention_user",
    "mention_user_nickname",
    "paste",
    "query_all_peps",
    "query_all_ruff_rules",
    "run_ruff_format",
)

_T = TypeVar("_T")


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


def format_ruff_rule(rule_data: RuffRule) -> FormattedRuffRule:
    """Format ruff rule data for embed-friendly output and append rule link.

    Args:
        rule_data: The ruff rule data.

    Returns:
        FormattedRuffRule: The formatted rule data.
    """
    explanation_formatted = re.sub(r"## (.+)", r"**\1**", rule_data["explanation"])
    rule_code = rule_data["code"]
    rule_name = rule_data["name"]
    rule_link = f"https://docs.astral.sh/ruff/rules/{rule_name}"
    rule_anchor_link = f"https://docs.astral.sh/ruff/rules/#{rule_code}"

    return {
        "name": rule_data.get("name", "No name available"),
        "summary": rule_data.get("summary", "No summary available"),
        "explanation": explanation_formatted,
        "fix": rule_data.get("fix", "No fix available"),
        "rule_link": rule_link,
        "rule_anchor_link": rule_anchor_link,
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
    result = subprocess.run(  # noqa: S603
        ["ruff", "format", "-"],  # noqa: S607
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
    """Naïve chunking of an iterable.

    Args:
        sequence (Iterable[_T]): Iterable to chunk
        size (int): Size of chunk

    Yields:
        Iterable[tuple[_T, ...]]: An n-tuple that contains chunked data
    """
    _sequence = iter(sequence)
    while chunk := tuple(islice(_sequence, size)):
        yield chunk


def format_resolution_link(resolution: str | None) -> str:
    """Formats the resolution URL into a markdown link.

    Args:
        resolution (str): The resolution URL.

    Returns:
        str: The formatted markdown link.
    """
    if not resolution:
        return "N/A"
    if "discuss.python.org" in resolution:
        return f"[via Discussion Forum]({resolution})"
    if "mail.python.org" in resolution:
        return f"[via Mailist]({resolution})"
    return resolution


async def query_all_peps() -> list[PEP]:
    """Query all PEPs from the PEPs Python.org API.

    Returns:
        list[PEP]: All PEPs
    """
    url = "https://peps.python.org/api/peps.json"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    return [  # type: ignore[reportReturnType]
        {
            "number": pep_info["number"],
            "title": pep_info["title"],
            "authors": pep_info["authors"].split(", "),
            "discussions_to": pep_info["discussions_to"],
            "status": PEPStatus(pep_info["status"]),
            "type": PEPType(pep_info["type"]),
            "topic": pep_info.get("topic", ""),
            "created": datetime.strptime(pep_info["created"], "%d-%b-%Y").replace(tzinfo=UTC).strftime("%Y-%m-%d"),
            "python_version": pep_info.get("python_version"),
            "post_history": pep_info.get("post_history", []),
            "resolution": format_resolution_link(pep_info.get("resolution", "N/A")),
            "requires": pep_info.get("requires"),
            "replaces": pep_info.get("replaces"),
            "superseded_by": pep_info.get("superseded_by"),
            "url": pep_info["url"],
        }
        for pep_info in data.values()
    ]


def get_next_friday(now: datetime, delay: int | None = None) -> tuple[datetime, datetime]:
    """Calculate the next Friday from ``now``.

    If ``delay``, calculate the Friday for ``delay`` weeks from now.

    Args:
        now: The current date and time.
        delay: The number of weeks to delay the calculation.

    Returns:
        datetime: The next Friday, optionally for the week after next.
    """
    days_ahead = 4 - now.weekday()
    if days_ahead < 0:
        days_ahead += 7
    if delay:
        days_ahead += 7 * delay
    start_dt = (now + dt.timedelta(days=days_ahead)).replace(hour=11, minute=0, second=0, microsecond=0)
    end_dt = start_dt + dt.timedelta(hours=1)
    return start_dt, end_dt
