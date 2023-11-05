"""Commands for testing purposes."""
from __future__ import annotations

from discord.ext import commands


class TestingCommands(commands.Cog):
    """Testing command cog."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Testing Commands"

    @commands.group(name="testing")
    async def testing(self, ctx: commands.Context) -> None:
        """Testing command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid testing command passed...")
            await ctx.send_help(ctx.command)

    @commands.command(
        name="ping",
        help="Run `!ping` or `!p` to get a `pong!` response.",
        aliases=["p"],
        brief="Run `!ping` or `!p` to get a `pong!` response.",
        description="Ping the bot.",
    )
    async def ping(self, ctx: commands.Context) -> None:
        """Ping the bot.

        Args:
            ctx: Context object.
        """
        print(f"pinged by {ctx.author}")
        guild = ctx.guild.id
        await ctx.send(f"pong to {guild}")


async def setup(bot: commands.Bot) -> None:
    """Add cog to bot.

    Args:
        bot: Bot object.
    """
    await bot.add_cog(TestingCommands(bot))
