"""Byte Bot."""
from __future__ import annotations

import contextlib
from pathlib import Path

import discord
from anyio import run
from discord import Activity, Intents
from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv

from src.byte.lib import settings
from src.byte.lib.logging import get_logger

__all__ = [
    "Byte",
    "run_bot",
]

logger = get_logger()
load_dotenv()


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
        dev_guild = discord.Object(id=settings.discord.DEV_GUILD_ID)
        self.tree.copy_global_to(guild=dev_guild)
        await self.tree.sync(guild=dev_guild)
        await self.load_cogs()

    async def load_cogs(self) -> None:
        """Load cogs."""
        cogs = []
        for plugins_dir in settings.discord.PLUGINS_DIRS:
            path = Path(plugins_dir)
            cogs.extend(path.glob("*.py"))

        cogs = [cog for cog in cogs if cog.stem != "__init__"]
        cogs_import_path = [f"{cog.parent.name}.{cog.stem}" for cog in cogs]

        for cog in cogs_import_path:
            with contextlib.suppress(commands.ExtensionAlreadyLoaded):
                await self.load_extension(cog)

    async def on_ready(self) -> None:
        """Handle bot ready event."""
        logger.info("%s has connected to Discord!", self.user)

    async def on_message(self, message: discord.Message) -> None:
        """Handle messages.

        Args:
            message: Message object.
        """
        await self.process_commands(message)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle command errors.

        Args:
            ctx: Context object.
            error: Error object.
        """


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
