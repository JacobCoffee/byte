"""Commands for GitHub."""
from __future__ import annotations

from discord.ext import commands

__all__ = ("GithubCommands", "setup")


class GithubCommands(commands.Cog):
    """GitHub command cog."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "GitHub Commands"

    @commands.hybrid_group(name="github")
    async def github(self, ctx: commands.Context) -> None:
        """GitHub command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid GitHub command passed...")
            await ctx.send_help(ctx.command)

    @commands.hybrid_command(
        name="repo",
        help="Run `!repo` or `!r` to get a link to the GitHub repository.",
        aliases=["r"],
        brief="Run `!repo` or `!r` to get a link to the GitHub repository.",
        description="Get a link to the GitHub repository.",
    )
    async def repo(self, ctx: commands.Context) -> None:
        """Get a link to the GitHub repository.

        Args:
            ctx: Context object.
        """
        await ctx.send("https://github.com/")


async def setup(bot: commands.Bot) -> None:
    """Add cog to bot.

    Args:
        bot: Bot object.
    """
    await bot.add_cog(GithubCommands(bot))
