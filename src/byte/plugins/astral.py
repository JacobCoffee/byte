"""Plugins for Astral Inc. related software, including Ruff, uv, etc."""
from __future__ import annotations

from discord import Embed, Interaction
from discord.app_commands import command as app_command
from discord.ext.commands import Bot, Cog

from byte.lib.common import ruff_logo
from byte.lib.utils import query_ruff_rule

__all__ = ("Astral", "setup")


class Astral(Cog):
    """Astral cog."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Astral Commands"

    @app_command(name="ruff")
    async def ruff_rule(self, interaction: Interaction, rule: str) -> None:
        """Slash command to lookup and display a Ruff linting rule.

        Args:
            interaction: Interaction object.
            rule: The rule to lookup.
        """
        await interaction.response.send_message("Querying Ruff rule...", ephemeral=True)

        rule_details = query_ruff_rule(rule)
        embed = Embed(title=f"Ruff Rule: {rule_details['name']}", color=0xD7FF64)
        embed.add_field(name="Summary", value=rule_details["summary"], inline=False)
        embed.add_field(name="Explanation", value=rule_details["explanation"], inline=False)
        if "fix" in rule_details:
            embed.add_field(name="Fix", value=rule_details["fix"], inline=False)
        if "rule_link" in rule_details:
            embed.add_field(
                name="Documentation", value=f"[Rule Documentation]({rule_details['rule_link']})", inline=False
            )
        embed.set_thumbnail(url=ruff_logo)

        await interaction.followup.send(embed=embed)

    @app_command(name="format")
    async def format_code(self, interaction: Interaction, code_block: str) -> None:
        """Formats the provided code using Ruff and uploads the result to a pastebin.

        Args:
            interaction: The Discord interaction object.
            code_block: The block of code to format.
        """
        await interaction.response.send_message("This feature is not yet ready.", ephemeral=True)
        # await interaction.response.send_message("Ruffing your code up...", ephemeral=True)
        # formatted_code = run_ruff_format(code_block)
        # paste_link = await paste(formatted_code)
        # await interaction.followup.send(f"I Ruffed your code up a little... {paste_link}", ephemeral=False)


async def setup(bot: Bot) -> None:
    """Set up the Events cog."""
    await bot.add_cog(Astral(bot))
