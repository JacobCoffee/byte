"""Commands for bot admins."""
from __future__ import annotations

from discord.ext import commands

from src.byte.checks import is_byte_dev_or_owner

__all__ = ("AdminCommands", "setup")


class AdminCommands(commands.Cog):
    """Commands for guild admins."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Admin Commands"  # type: ignore[misc]

    @commands.group(name="admin")
    @is_byte_dev_or_owner()
    async def admin(self, ctx: commands.Context) -> None:
        """Commands for bot admins."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid admin command passed...")
            await ctx.send_help(ctx.command)

    @commands.command(name="list-cogs", help="Lists all loaded cogs.", aliases=["lc"], hidden=True)
    @commands.is_owner()
    async def list_cogs(self, ctx: commands.Context) -> None:
        """Lists all loaded cogs.

        Args:
            ctx: Context object.
        """
        cogs = [cog.split(".")[-1] for cog in self.bot.extensions]
        await ctx.send(f"Loaded cogs: {', '.join(cogs)}")

    @commands.command(name="reload", help="Reloads a cog.", aliases=["rl"], hidden=True)
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, cog: str = "all") -> None:
        """Reloads a cog or all cogs if specified.

        Args:
            ctx: Context object.
            cog: Name of cog to reload. Default is "all".
        """
        if cog.lower() == "all":
            await self.reload_all_cogs(ctx)
        else:
            await self.reload_single_cog(ctx, cog)

    async def reload_all_cogs(self, ctx: commands.Context) -> None:
        """Reload all cogs.

        Args:
            ctx: Context object.
        """
        extensions = list(self.bot.extensions.keys())
        results = []

        for extension in extensions:
            extension_name = extension[9:]
            result = await self.reload_single_cog(ctx, extension_name, send_message=False)
            results.append(result)

        results.append("All cogs reloaded!")
        await ctx.send("\n".join(results))

    async def reload_single_cog(self, ctx: commands.Context, cog: str, send_message: bool = True) -> str:
        """Reload a single cog."""
        try:
            await self.bot.reload_extension(f"commands.{cog}")
            message = f"Cog `{cog}` reloaded!"
        except (commands.ExtensionNotLoaded, commands.ExtensionNotFound) as e:
            message = f"Error with cog `{cog}`: {e!s}"

        if send_message:
            await ctx.send(message)

        return message


async def setup(bot: commands.Bot) -> None:
    """Add cog to bot.

    Args:
        bot: Bot object.
    """
    await bot.add_cog(AdminCommands(bot))
