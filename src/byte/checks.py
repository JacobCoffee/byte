"""Validation checks."""
from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext.commands import Context, check
from dotenv import load_dotenv

from src.server.lib import settings

if TYPE_CHECKING:
    from discord import Member

load_dotenv()

__all__ = ["is_byte_dev_or_owner"]


def is_byte_dev_or_owner() -> check:
    """Check if the user is the bot owner, has the "byte-dev" role, or matches a specific user ID.

    Returns:
        check: The check to be used in a command.
    """

    async def predicate(ctx: Context) -> bool:
        """Check if the user is the bot owner, has the "byte-dev" role, or matches a specific user ID.

        Args:
            ctx: The context of the command.

        Returns:
            bool: Whether the user is the bot owner, has the "byte-dev" role, or matches a specific user ID.
        """
        if await ctx.bot.is_owner(ctx.author) or ctx.author.id == settings.discord.DEV_USER_ID:
            return True

        member: Member = ctx.author
        return any(role.name == "byte-dev" for role in member.roles)

    return check(predicate)
