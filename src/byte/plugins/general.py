"""General plugins to be used wherever."""

from __future__ import annotations

from discord import Embed, Interaction
from discord.app_commands import command as app_command
from discord.ext.commands import Bot, Cog

from byte.lib.common.assets import litestar_logo_yellow
from byte.lib.common.links import markdown_guide, pastebin
from byte.lib.utils import linker

__all__ = ("GeneralCommands", "setup")


class GeneralCommands(Cog):
    """General commands."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "General Commands"  # type: ignore[misc]

    @app_command(name="paste")
    async def show_paste(self, interaction: Interaction) -> None:
        """Slash command to show an embed for pasting code.

        Args:
            interaction: Interaction object.
        """
        embed = Embed(title="Paste long format code", color=0x42B1A8)
        embed.add_field(
            name="Paste Service",
            value=f"You can easily paste long code by using the {linker('Paste', pastebin)} service.",
            inline=True,
        )
        embed.add_field(
            name="Syntax Highlighting",
            value="You can also use backticks to format your code. Read about it in the "
            f"{linker('Discord Markdown Guide', markdown_guide)}.",
        )
        embed.set_thumbnail(url=litestar_logo_yellow)

        await interaction.response.send_message(embed=embed)


async def setup(bot: Bot) -> None:
    """Set up the General cog."""
    await bot.add_cog(GeneralCommands(bot))
