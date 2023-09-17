"""Discord Bot."""

from __future__ import annotations

import contextlib
from pathlib import Path

import discord
from discord.ext import commands
from discord.ext.commands import MemberNotFound
from dotenv import load_dotenv

from src.server.lib import settings

__all__ = ("run",)


load_dotenv()


def run() -> None:
    """Run bot."""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix=settings.discord.COMMAND_PREFIX, intents=intents)

    @bot.event
    async def on_ready() -> None:
        """Event handler for a bots ready state."""
        print(f"{bot.user} has connected to Discord!")
        cogs = []
        for command_dir in map(Path, settings.discord.COMMANDS_DIRS):
            cogs.extend(command_dir.glob("*.py"))

        cogs = [cog for cog in cogs if cog.stem != "__init__"]
        cogs_import_path = [f"{cog.parent.name}.{cog.stem}" for cog in cogs]

        for cog in cogs_import_path:
            with contextlib.suppress(commands.ExtensionAlreadyLoaded):
                await bot.load_extension(cog)
        print(f"Bot is ready with {len(cogs_import_path)} cogs added: {cogs_import_path}")
        print(f"Discord Settings: {settings.discord.__dict__}")
        print(settings.discord.DEV_GUILD_ID)
        bot.tree.copy_global_to(guild=discord.Object(id=settings.discord.DEV_GUILD_ID))
        await bot.tree.sync(guild=discord.Object(id=settings.discord.DEV_GUILD_ID))

    @bot.event
    async def on_message(message: discord.Message) -> None:
        """Event handler for messages.

        Args:
            message: Message object.
        """
        await bot.process_commands(message)

    @bot.event
    async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
        """Global error handler.

        Args:
            ctx: Context object.
            error: Error object.
        """
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"Oh no! I couldn't find the command `{ctx.invoked_with}` :cry:")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"It looks like you forgot to pass in `{error.param.name}`!")
        elif isinstance(error, MemberNotFound):
            await ctx.send(f"Well shit... I couldn't find the user `{error.argument}`... maybe they left the server?")
        else:
            await ctx.send(f"Something bad happened! Error: {error!r}")
            raise error

    @bot.event
    async def on_thread_create(thread: discord.Thread) -> None:
        if thread.parent.name == "help":
            reply = (
                f"At your assistance, {thread.owner.mention}.\n"
                f"Make sure you include an [MCVE](https://stackoverflow.com/help/minimal-reproducible-example) in "
                f"your post.\n"
                f"When you are done you can tag your post as ***✅ Solved***!\n"
                f"If no one responds within 4 hours, please ping `@Member`."
            )
            await thread.send(reply)
        if thread.parent.name == "forum":
            reply = f"Thanks for posting, {thread.owner.mention}!"
            await thread.send(reply)

    @bot.tree.context_menu(name="Get user data")
    async def get_user_data(interaction: discord.Interaction, member: discord.Member) -> None:
        """Get user data."""
        embed = discord.Embed(color=member.color, timestamp=interaction.created_at)
        embed.set_author(name=f"User Info - {member}")
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=member.avatar.url)
        embed.add_field(name="ID:", value=member.id)
        embed.add_field(name="Guild name:", value=interaction.guild.name)
        embed.add_field(name="Nickname:", value=member.display_name)
        embed.add_field(name="Created at:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="Bot?", value=member.bot)
        embed.add_field(name="Top role:", value=member.top_role.mention)
        embed.add_field(name="Status:", value=member.status)
        embed.add_field(name="Activity:", value=member.activity)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="message")
    async def send_message(interaction: discord.Interaction, message: str) -> None:
        """Send a message."""
        await interaction.response.send_message(message)

    bot.run(settings.discord.API_TOKEN.get_secret_value())


if __name__ == "__main__":
    run()
