"""Plugins related to forums."""

import discord
from discord import Embed, Interaction, Member, Thread
from discord.app_commands import command as app_command
from discord.ext.commands import Bot, Cog, Context, command, hybrid_command

from byte_bot.byte.lib.common.assets import litestar_logo_yellow
from byte_bot.byte.lib.common.links import mcve
from byte_bot.byte.lib.utils import linker

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
        _tags_per_post = 5
        if isinstance(ctx.channel, Thread) and ctx.channel.parent.name == "help":
            if solved_tag := discord.utils.find(lambda t: t.name == _solved_tag, ctx.channel.parent.available_tags):
                if len(ctx.channel.applied_tags) == _tags_per_post and solved_tag not in ctx.channel.applied_tags:
                    # Tags per post are limited to 5
                    # Remove a tag to make room for "Solved"
                    await ctx.channel.remove_tags(ctx.channel.applied_tags[-1])
                await ctx.channel.add_tags(solved_tag, reason="Marked as solved.")
                await ctx.send("Marked as solved and closed the help forum!", ephemeral=True)
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

    @app_command(name="mcve")
    async def tree_sync(self, interaction: Interaction, user: Member) -> None:
        """Slash command to request an MCVE from a user.

        Args:
            interaction: Interaction object.
            user: The user to target with the MCVE request.
        """
        await interaction.response.send_message("Processing request...", ephemeral=True)

        embed = Embed(title="MCVE Needed to Reproduce!", color=0x42B1A8)
        embed.add_field(name="Hi", value=f"{user.mention}", inline=True)
        embed.add_field(
            name="MCVE",
            value=f"Please include an {linker('MCVE', mcve)} so that we can reproduce your issue locally.",
            inline=True,
        )
        embed.set_thumbnail(url=litestar_logo_yellow)

        await interaction.followup.send(embed=embed)


async def setup(bot: Bot) -> None:
    """Add cog to bot.

    Args:
        bot: Bot object.
    """
    await bot.add_cog(ForumCommands(bot))
