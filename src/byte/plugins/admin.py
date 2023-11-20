"""Plugins for admins.

.. todo:: add an unload cog command.
"""
from discord import Interaction
from discord.app_commands import command as app_command
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context, command, group, is_owner

from src.byte.lib.utils import is_byte_dev_or_owner

__all__ = ("AdminCommands", "setup")


class AdminCommands(Cog):
    """Admin command cog."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Admin Commands"  # type: ignore[misc]

    @group(name="admin")
    @is_byte_dev_or_owner()
    async def admin(self, ctx: Context) -> None:
        """Commands for bot admins."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid admin command passed...")
            await ctx.send_help(ctx.command)

    @command(name="list-cogs", help="Lists all loaded cogs.", aliases=["lc"], hidden=True)
    @is_owner()
    async def list_cogs(self, ctx: Context) -> None:
        """Lists all loaded cogs.

        Args:
            ctx: Context object.
        """
        cogs = [cog.split(".")[-1] for cog in self.bot.extensions]
        await ctx.send(f"Loaded cogs: {', '.join(cogs)}")

    @command(name="reload", help="Reloads a cog.", aliases=["rl"], hidden=True)
    @is_owner()
    async def reload(self, ctx: Context, cog: str = "all") -> None:
        """Reloads a cog or all cogs if specified.

        Args:
            ctx: Context object.
            cog: Name of cog to reload. Default is "all".
        """
        if cog.lower() == "all":
            await self.reload_all_cogs(ctx)
        else:
            await self.reload_single_cog(ctx, cog)

    async def reload_all_cogs(self, ctx: Context) -> None:
        """Reload all cogs.

        Args:
            ctx: Context object.
        """
        results = []
        for extension in list(self.bot.extensions):
            cog_name = extension.split(".")[-1]
            result = await self.reload_single_cog(ctx, cog_name, send_message=False)
            results.append(result)
        results.append("All cogs reloaded!")
        await ctx.send("\n".join(results))

    async def reload_single_cog(self, ctx: Context, cog: str, send_message: bool = True) -> str:
        """Reload a single cog."""
        try:
            await self.bot.reload_extension(f"plugins.{cog}")
            message = f"Cog `{cog}` reloaded!"
        except (commands.ExtensionNotLoaded, commands.ExtensionNotFound) as e:
            message = f"Error with cog `{cog}`: {e!s}"

        if send_message:
            await ctx.send(message)

        return message

    @app_command(name="sync")
    @is_byte_dev_or_owner()
    async def tree_sync(self, interaction: Interaction) -> None:
        """Slash command to perform a global sync."""
        results = await self.bot.tree.sync()
        await interaction.response.send_message("\n".join(i.name for i in results), ephemeral=True)


async def setup(bot: Bot) -> None:
    """Add cog to bot.

    Args:
        bot: Bot object.
    """
    await bot.add_cog(AdminCommands(bot))
