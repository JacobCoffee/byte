"""Inheritable views that include extra functionality for base Views classes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ButtonStyle, Embed, Interaction
from discord.ui import Button, View, button

if TYPE_CHECKING:
    from typing import Self

    from discord.ext.commands import Bot

__all__ = ("BaseEmbedView",)


class BaseEmbedView(View):
    """Base view including common buttons."""

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

    async def delete_button_callback(self, interaction: Interaction) -> None:
        """Delete the message this view is attached to.

        Args:
            interaction: Interaction object.
        """
        if await self.interaction_check(interaction):
            await interaction.message.delete()

    async def learn_more_button_callback(self, interaction: Interaction) -> None:
        """Send the original embed to the user privately.

        Args:
            interaction: Interaction object.
        """
        await interaction.response.send_message(embed=self.original_embed, ephemeral=True)

    @button(label="Delete", style=ButtonStyle.red, custom_id="delete_button")
    async def delete_button(self, interaction: Interaction, _: Button[Self]) -> None:
        """Button to delete the message this view is attached to.

        Args:
            interaction: Interaction object.
            _: Button object.
        """
        await self.delete_button_callback(interaction)

    @button(label="Learn More", style=ButtonStyle.green, custom_id="learn_more_button")
    async def learn_more_button(self, interaction: Interaction, _: Button[Self]) -> None:
        """Button to privately message the requesting user the full embed.

        Args:
            interaction: Interaction object.
            _: Button object.
        """
        await self.learn_more_button_callback(interaction)
