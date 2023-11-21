"""Byte utilities."""
from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

from src.byte.lib import settings

if TYPE_CHECKING:
    from typing import Any

    from discord.ext.commands import Context
    from discord.ext.commands._types import Check

__all__ = ("is_byte_dev",)


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
