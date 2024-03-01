"""Discord UI views used in Astral commands."""
from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ui import View

from byte.lib.log import get_logger

if TYPE_CHECKING:
    from discord import Embed, Interaction
    from discord.ext.commands import Bot

__all__ = ("RuffView",)

logger = get_logger()


class RuffView(View):
    """View for the Ruff embed."""

    def __init__(self, author: int, bot: Bot, original_embed: Embed, minified_embed: Embed, *args, **kwargs) -> None:
        """Initialize the view.

        Args:
            author: Author ID.
            bot: Bot object.
            original_embed: The original embed to display.
            minified_embed: The minified embed to display.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.author_id = author
        self.bot = bot
        self.original_embed = original_embed
        self.minified_embed = minified_embed

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Check if the user is the author or a guild admin.

        Args:
            interaction: Interaction object.

        Returns:
            True if the user is the author or a guild admin, False otherwise.
        """
        if interaction.user.id == self.author_id or interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message(
            "You do not have permission to interact with this message.", ephemeral=True
        )
        return False
