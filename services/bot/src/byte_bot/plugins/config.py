"""Plugins for guild admins to configure Byte and its features."""

from __future__ import annotations

from typing import TYPE_CHECKING

from discord.app_commands import Choice, autocomplete
from discord.app_commands import command as app_command
from discord.ext.commands import Bot, Cog

from byte_bot.lib.common import config_options
from byte_bot.views.config import ConfigView

if TYPE_CHECKING:
    from discord import Interaction

__all__ = ("Config", "setup")


class Config(Cog):
    """Config cog."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Config Commands"
        self.config_options = config_options

    async def _config_autocomplete(self, interaction: Interaction, current: str) -> list[Choice[str]]:  # noqa: ARG002
        """Autocomplete config for the config dropdown (up?) slash command."""
        return [
            Choice(name=f"{option['label']} - {option['description']}", value=option["label"])
            for option in config_options
            if current.lower() in option["label"].lower()
        ][:25]

    @app_command(name="config")
    @autocomplete(setting=_config_autocomplete)
    async def config_rule(self, interaction: Interaction, setting: str | None = None) -> None:
        """Slash command to configure Byte.

        Args:
            interaction: Interaction object.
            setting: The setting to configure.
        """
        if setting:
            if selected_option := next(
                (option for option in config_options if option["label"] == setting),
                None,
            ):
                view = ConfigView(preselected=selected_option["label"])
                await interaction.response.send_message(
                    f"Configure {selected_option['label']}:",
                    view=view,
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    f"Invalid setting: {setting}. Please select a valid setting.",
                    ephemeral=True,
                )
        else:
            view = ConfigView()
            await interaction.response.send_message("Select a configuration option:", view=view, ephemeral=True)


async def setup(bot: Bot) -> None:
    """Set up the config cog."""
    await bot.add_cog(Config(bot))
