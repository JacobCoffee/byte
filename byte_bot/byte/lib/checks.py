""":doc:`Checks <discord.py:Checks>` for Byte."""

from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext.commands import CheckFailure, Context, check

from byte.lib import settings

if TYPE_CHECKING:
    from collections.abc import Callable

    from discord.ext.commands._types import Check

__all__ = ("is_byte_dev", "is_guild_admin")


def is_guild_admin() -> Callable[[Context], Check]:
    """Check if the user is a guild admin.

    Returns:
        A check function.
    """

    async def predicate(ctx: Context) -> bool:
        """Check if the user is a guild admin.

        Args:
            ctx: Context object.

        Returns:
            True if the user is a guild admin, False otherwise.
        """
        if not (member := ctx.guild.get_member(ctx.author.id)):
            msg = "Member not found in the guild."
            raise CheckFailure(msg)
        return member.guild_permissions.administrator

    return check(predicate)


def is_byte_dev() -> Callable[[Context], Check]:
    """Determines if the user is a Byte developer or owner.

    Returns:
        A check function.
    """

    async def predicate(ctx: Context) -> bool:
        """Check if the user is a Byte developer or owner.

        Args:
            ctx: Context object.

        Returns:
            True if the user is a Byte developer or owner, False otherwise.
        """
        return (
            await ctx.bot.is_owner(ctx.author)
            or ctx.author.id == settings.discord.DEV_USER_ID
            or any(role.name == "byte-dev" for role in ctx.author.roles)
        )

    return check(predicate)
