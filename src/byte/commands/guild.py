"""Commands for a guild."""
from __future__ import annotations

import discord
from discord import ForumTag, Thread
from discord.ext import commands

__all__ = ("GuildCommands", "setup")


class GuildCommands(commands.Cog):
    """Guild command cog."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Guild Commands"

    @commands.group(name="guild")
    async def guild(self, ctx: commands.Context) -> None:
        """Guild command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid guild command passed...")
            await ctx.send_help(ctx.command)

    @guild.command(
        name="user",
        help="Run `!user` or `!u` to get user information.",
        aliases=["u"],
        brief="Run `!user` or `!u` to get user information.",
        description="Get user information.",
    )
    async def get_user(self, ctx: commands.Context, member: discord.Member = None) -> None:
        """Get user information.

        Args:
            ctx: Context object.
            member: Member object.
        """
        if member is None:
            member = ctx.author

        embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)

        roles = [role for role in member.roles if role != ctx.guild.default_role]
        embed.set_author(name=f"User Info - {member}")
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.add_field(name="ID:", value=member.id)
        embed.add_field(name="Guild name:", value=ctx.guild.name)
        embed.add_field(name="Nickname:", value=member.display_name)
        embed.add_field(name="Created at:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name=f"Roles ({len(roles)})", value=" ".join([role.mention for role in roles]))
        embed.add_field(name="Top role:", value=member.top_role.mention)
        embed.add_field(name="Bot?", value=member.bot)

        await ctx.send(embed=embed)

    @guild.command()
    async def react(self, ctx: commands.Context) -> None:
        """React to the command message with a check mark.

        Args:
            ctx: Context object.
        """
        await ctx.message.add_reaction("✅")

    @commands.hybrid_command(
        name="solve",
        help="Run `!solve` or `!s` to mark a forum post as solved and close it.",
        aliases=["s"],
        brief="Run `!solve` or `!s` to mark a forum post as solved and close it.",
        description="Mark a forum post as solved and close it.",
    )
    async def solved(self, ctx: commands.Context) -> None:
        """Mark the forum post as solved and close it."""
        if isinstance(ctx.channel, Thread) and ctx.channel.parent.name == "help":
            solved_tag = ForumTag(name="Solved", emoji="✅")
            await ctx.channel.add_tags(solved_tag)
            await ctx.send("Marked as solved and closed the help forum!")
            await ctx.channel.edit(archived=True)
        else:
            await ctx.send("This command can only be used in the help forum.")

    @guild.command()
    async def tags(self, ctx: commands.Context) -> None:
        """Get all tags in the channel.

        Args:
            ctx: Context object.
        """
        tags = ctx.channel.applied_tags
        await ctx.send(f"Tags in this channel: {', '.join([tag.name for tag in tags])}")


async def setup(bot: commands.Bot) -> None:
    """Add cog to bot.

    Args:
        bot: Bot object.
    """
    await bot.add_cog(GuildCommands(bot))
