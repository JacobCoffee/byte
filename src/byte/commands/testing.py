"""Commands for testing purposes."""
from __future__ import annotations

from discord import Embed
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
        print(f"pinged by {ctx.author}")  # noqa: T201
        guild = ctx.guild.id
        await ctx.send(f"pong to {guild}")

    @commands.command(name="gethelp")
    async def helpme(self, ctx: commands.Context) -> None:
        """Provides help resources in a card-style embed with a thumbnail."""
        issues = "https://github.com/litestar-org/litestar/issues"
        embed = Embed(title="Need Help?", color=0x42B1A8)  # Updated color to #42b1a8
        embed.add_field(name="GitHub Issues", value=f"[Click here to report an issue]({issues})")
        embed.add_field(name="Help Channel", value="<#1064114019373432912>")
        embed.set_footer(text="Please provide a Minimal, Complete, and Verifiable example (MCVE) if applicable.")
        embed.set_thumbnail(
            url="https://github.com/litestar-org/branding/blob/main/assets/Branding%20-%20PNG%20-%20Transparent/Badge%20-%20White.png?raw=true"
        )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Add cog to bot.

    Args:
        bot: Bot object.
    """
    await bot.add_cog(TestingCommands(bot))
