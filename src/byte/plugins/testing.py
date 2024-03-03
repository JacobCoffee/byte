"""Plugins for testing purposes."""
from discord.ext.commands import Bot, Cog, Context, command, group


class TestCog(Cog, name="Ping"):
    """Testing commands."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Testing Commands"

    @group(name="testing")
    async def testing(self, ctx: Context) -> None:
        """Testing command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Hey, uh... {ctx.subcommand_passed} is not a valid testing command {ctx.author.mention}...")
            await ctx.send_help(ctx.command)

    @command(
        name="ping",
        help="Run `!ping` or `!p` to get a `pong!` response.",
        aliases=["p"],
        brief="Run `!ping` or `!p` to get a `pong!` response.",
        description="Ping the bot.",
    )
    async def ping(self, ctx: Context) -> None:
        """Responds with 'pong'."""
        assert ctx.guild, "Can this be None?"
        await ctx.send(f"pong to the {ctx.guild.name} guild!")


async def setup(bot: Bot) -> None:
    """Load the Testing cog."""
    await bot.add_cog(TestCog(bot))
