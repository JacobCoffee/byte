"""Plugins related to forums."""
import discord
from discord import Thread
from discord.ext.commands import Bot, Cog, Context, command, hybrid_command

__all__ = ("ForumCommands", "setup")


class ForumCommands(Cog):
    """Forum command cog."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Forum Commands"

    @hybrid_command(
        name="solve",
        help="Run `!solve` or `!s` to mark a forum post as solved and close it.",
        aliases=["s"],
        brief="Run `!solve` or `!s` to mark a forum post as solved and close it.",
        description="Mark a forum post as solved and close it.",
    )
    async def solved(self, ctx: Context) -> None:
        """Mark the forum post as solved and close it.

        .. todo: Parameterize the tag name and allow each guild to assign it
            in placed of "Solved" (Default can stay as solved, though)

        .. todo:: Parameterize the channel name (default of help, still).
            Also, allow for a list of channels to be specified.
            users may want to be able to mark things solved/closed in
            Help, Suggestions, Showcase, etc. (or any other forum channel)
        """
        _solved_tag = "Solved"
        if isinstance(ctx.channel, Thread) and ctx.channel.parent.name == "help":
            if solved_tag := discord.utils.find(lambda t: t.name == _solved_tag, ctx.channel.parent.available_tags):
                await ctx.channel.add_tags(solved_tag, reason="Marked as solved.")
                await ctx.send("Marked as solved and closed the help forum!")
                await ctx.channel.edit(archived=True)
            else:
                await ctx.send(f"'{_solved_tag}' tag not found.")
        else:
            await ctx.send("This command can only be used in the help forum.")

    @command()
    async def tags(self, ctx: Context) -> None:
        """Get all tags in the channel.

        Args:
            ctx: Context object.
        """
        tags = ctx.channel.applied_tags
        await ctx.send(f"Tags in this channel: {', '.join([tag.name for tag in tags])}")


async def setup(bot: Bot) -> None:
    """Add cog to bot.

    Args:
        bot: Bot object.
    """
    await bot.add_cog(ForumCommands(bot))
