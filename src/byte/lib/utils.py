"""Byte utilities."""
from discord.ext import commands
from discord.ext.commands import Context, check

from src.byte.lib import settings

__all__ = ("is_byte_dev_or_owner",)


def is_byte_dev_or_owner() -> check:
    """Check if the user is a Byte Dev or Owner.

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
