"""Discord UI views used in Astral commands."""
from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ButtonStyle, Embed, Interaction
from discord.ui import Button, View, button

from byte.lib.log import get_logger

if TYPE_CHECKING:
    from typing import Self

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

    @staticmethod
    async def delete_button_callback(interaction: Interaction) -> None:
        """Delete the message this view is attached to.

        Args:
            interaction: Interaction object.
        """
        await interaction.message.delete()

    async def collapse_button_callback(self, interaction: Interaction) -> None:
        """Minify the message to show less information but not none.

        Args:
            interaction: Interaction object.
            button: Button object.
        """
        await interaction.response.edit_message(embed=self.minified_embed, view=self)

    async def expand_button_callback(self, interaction: Interaction) -> None:
        """Expand the message to show full information.

        Args:
            interaction: Interaction object.
            button: Button object.
        """
        await interaction.message.edit(embed=self.original_embed, view=self)

    # Define buttons using decorators
    @button(label="Delete", style=ButtonStyle.red, custom_id="delete_button")
    async def delete_button(self, interaction: Interaction, button: Button[Self]) -> None:
        """Button to delete the message this view is attached to.

        Args:
            interaction: Interaction object.
            button: Button object.
        """
        await self.delete_button_callback(interaction)

    @button(label="Collapse", style=ButtonStyle.grey, custom_id="collapse_button")
    async def collapse_button(self, interaction: Interaction, button: Button[Self]) -> None:
        """Button to minify the embed to show less information but not none.

        Args:
            interaction: Interaction object.
            button: Button object.
        """
        await self.collapse_button_callback(interaction)

    @button(label="Expand", style=ButtonStyle.green, custom_id="expand_button", disabled=True)
    async def expand_button(self, interaction: Interaction, button: Button[Self]) -> None:
        """Button to expand the embed to show full information.

        Args:
            interaction: Interaction object.
            button: Button object.
        """
        await self.expand_button_callback(interaction, button)
