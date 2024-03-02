"""Plugins for Python related things, including PyPI, PEPs, etc."""
from __future__ import annotations

from discord import Embed, Interaction
from discord.app_commands import Choice, autocomplete
from discord.app_commands import command as app_command
from discord.ext.commands import Bot, Cog

from byte.lib.common.assets import python_logo
from byte.lib.common.colors import python_blue, python_yellow
from byte.lib.utils import PEP, query_all_peps
from byte.views.embed import ExtendedEmbed, Field
from byte.views.python import PEPView

__all__ = ("Python", "setup")


class Python(Cog):
    """Python cog."""

    def __init__(self, bot: Bot, peps: list[PEP]) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Python Commands"
        self._peps = {pep["number"]: pep for pep in peps}

    async def _pep_autocomplete(self, interaction: Interaction, current_pep: str) -> list[Choice[str]]:  # noqa: ARG002
        """Autocomplete for PEP numbers and titles.

        .. warning:: ``interaction`` is not used, but is required.
        """
        return [
            Choice(name=f'PEP {number} - {pep["title"]}', value=str(number))
            for number, pep in self._peps.items()
            if current_pep.lower() in str(number) or current_pep.lower() in pep["title"].lower()
        ][:25]

    @app_command(name="pep")
    @autocomplete(pep=_pep_autocomplete)
    async def peps(self, interaction: Interaction, pep: int) -> None:
        """Slash command to look up and display a Python Enhancement Proposal (PEP).

        Args:
            interaction: Interaction object.
            pep: The PEP number to lookup.
        """
        await interaction.response.send_message(f"Querying PEP {pep}...", ephemeral=True)

        if (pep_details := self._peps.get(pep)) is None:
            embed = Embed(title=f"PEP #{pep} not found... Maybe you should submit it!", color=python_yellow)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        docs_field = f"- [PEP Documentation]({pep_details['url']})\n"

        fields = [
            Field(name="Summary", value=pep_details["title"], inline=False),
            Field(name="Status", value=pep_details["status"], inline=True),
            Field(name="Type", value=pep_details["type"], inline=True),
            Field(name="Authors", value=", ".join(pep_details["authors"]), inline=False),
            Field(name="Created", value=str(pep_details["created"]), inline=True),
            Field(name="Python Version", value=pep_details["python_version"], inline=True),
            Field(name="Documentation", value=docs_field, inline=False),
        ]
        minified_embed = ExtendedEmbed.from_field_dicts(
            title=f"PEP #{pep_details['number']}", color=python_blue, fields=fields
        )
        minified_embed.set_thumbnail(url=python_logo)
        embed = minified_embed.deepcopy()
        view = PEPView(author=interaction.user.id, bot=self.bot, original_embed=embed, minified_embed=minified_embed)
        await interaction.followup.send(embed=minified_embed, view=view)


async def setup(bot: Bot) -> None:
    """Set up the Python cog."""
    await bot.add_cog(Python(bot, await query_all_peps()))
