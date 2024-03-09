"""Plugins for guild admins to configure Byte and its features."""
from __future__ import annotations

from typing import TYPE_CHECKING

from discord.app_commands import command as app_command
from discord.ext.commands import Bot, Cog

from byte.views.config import ConfigView

if TYPE_CHECKING:
    from discord import Interaction

__all__ = ("Config", "setup")


class Config(Cog):
    """Config cog."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Config Commands"

    @app_command(name="config")
    async def config_rule(self, interaction: Interaction) -> None:
        """Slash command to configure Byte.

        Args:
            interaction: Interaction object.
        """
        view = ConfigView()
        await interaction.response.send_message("Select a configuration option:", view=view, ephemeral=True)


async def setup(bot: Bot) -> None:
    """Set up the config cog."""
    await bot.add_cog(Config(bot))
