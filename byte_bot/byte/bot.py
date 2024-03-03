"""Byte Bot."""

from __future__ import annotations

import contextlib

import discord
import httpx
from anyio import run
from discord import Activity, Forbidden, Intents, Member, Message, NotFound
from discord.ext.commands import Bot, CommandError, Context, ExtensionAlreadyLoaded
from dotenv import load_dotenv
from httpx import ConnectError

from byte_bot.byte.lib import settings
from byte_bot.byte.lib.log import get_logger

__all__ = [
    "Byte",
    "run_bot",
]

logger = get_logger()
load_dotenv()


async def on_member_join(member: Member) -> None:
    """Handle member join event.

    Args:
        member: Member object.
    """
    await member.send(
        f"Welcome to {member.guild.name}! Please make sure to read the rules if you haven't already. "
        f"Feel free to ask any questions you have in the help channel."
    )


class Byte(Bot):
    """Byte Bot Base Class."""

    def __init__(self, command_prefix: list[str], intents: Intents, activity: Activity) -> None:
        """Initialize the bot.

        Args:
            command_prefix (str): Command prefix for the bot.
            intents (discord.Intents): Intents for the bot.
            activity (discord.Activity): Activity for the bot.
        """
        super().__init__(command_prefix=command_prefix, intents=intents, activity=activity)

    async def setup_hook(self) -> None:
        """Any setup we need can be here."""
        # Load cogs before syncing the tree.
        await self.load_cogs()
        dev_guild = discord.Object(id=settings.discord.DEV_GUILD_ID)
        self.tree.copy_global_to(guild=dev_guild)
        await self.tree.sync(guild=dev_guild)

    async def load_cogs(self) -> None:
        """Load cogs."""
        cogs = [
            cog
            for plugins_dir in settings.discord.PLUGINS_DIRS
            for cog in plugins_dir.rglob("*.py")
            if cog.stem != "__init__"
        ]

        cogs_import_path = [".".join(cog.parts[cog.parts.index("byte_bot") : -1]) + "." + cog.stem for cog in cogs]

        for cog in cogs_import_path:
            with contextlib.suppress(ExtensionAlreadyLoaded):
                await self.load_extension(cog)

    async def on_ready(self) -> None:
        """Handle bot ready event."""
        logger.info("%s has connected to Discord!", self.user)

    async def on_message(self, message: Message) -> None:
        """Handle message events.

        Args:
            message: Message object.
        """
        await self.process_commands(message)

    async def on_command_error(self, ctx: Context, error: CommandError) -> None:
        """Handle command errors.

        Args:
            ctx: Context object.
            error: Error object.
        """
        err = error.original if hasattr(error, "original") else error
        if isinstance(err, Forbidden | NotFound):
            return

        embed = discord.Embed(title="Command Error", description=str(error), color=discord.Color.red())
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.add_field(name="Command", value=ctx.command)
        embed.add_field(name="Message", value=ctx.message.content)
        embed.add_field(name="Channel", value=ctx.channel.mention)
        embed.add_field(name="Author", value=ctx.author.mention)
        embed.add_field(name="Guild", value=ctx.guild.name)
        embed.add_field(name="Location", value=f"[Jump]({ctx.message.jump_url})")
        embed.set_footer(text=f"Time: {ctx.message.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        await ctx.send(embed=embed, ephemeral=True)

    @staticmethod
    async def on_member_join(member: Member) -> None:
        """Handle member join event.

        Args:
            member: Member object.
        """
        if not member.bot:
            await member.send(
                f"Welcome to {member.guild.name}! Please make sure to read the rules if you haven't already. "
                f"Feel free to ask any questions you have in the help channel."
            )

    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Handle guild join event.

        Args:
            guild: Guild object.
        """
        await self.tree.sync(guild=guild)
        api_url = f"http://0.0.0.0:8000/api/guilds/create?guild_id={guild.id}&guild_name={guild.name}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(api_url)

                if response.status_code == httpx.codes.CREATED:
                    logger.info("successfully added guild %s (id: %s)", guild.name, guild.id)
                    embed = discord.Embed(
                        title="Guild Joined",
                        description=f"Joined guild {guild.name} (ID: {guild.id})",
                        color=discord.Color.green(),
                    )
                else:
                    embed = discord.Embed(
                        title="Guild Join Failed",
                        description=f"Joined guild, but failed to add guild {guild.name} (ID: {guild.id}) to database",
                        color=discord.Color.red(),
                    )

                if dev_guild := self.get_guild(settings.discord.DEV_GUILD_ID):
                    if dev_channel := dev_guild.get_channel(settings.discord.DEV_GUILD_INTERNAL_ID):
                        await dev_channel.send(embed=embed)
                    else:
                        logger.error("dev channel not found.")
                else:
                    logger.error("dev guild not found.")
        except ConnectError:
            logger.exception("failed to connect to api to add guild %s (id: %s)", guild.name, guild.id)


def run_bot() -> None:
    """Run the bot."""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    presence = discord.Activity(
        name="!help",
        type=discord.ActivityType.custom,
        state="Serving Developers",
        details="!help",
        url=settings.discord.PRESENCE_URL,
    )
    bot = Byte(command_prefix=settings.discord.COMMAND_PREFIX, intents=intents, activity=presence)

    async def start_bot() -> None:
        """Start the bot."""
        await bot.start(settings.discord.TOKEN)

    run(start_bot)


if __name__ == "__main__":
    run_bot()
