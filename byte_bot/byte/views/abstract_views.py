"""Inheritable views that include extra functionality for base Views classes."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any, Literal, ParamSpec, TypedDict

from discord import ButtonStyle, Colour, Embed, Interaction
from discord.ui import Button, View, button

if TYPE_CHECKING:
    from datetime import datetime
    from typing import NotRequired, Self

    from discord.ext.commands import Bot

__all__ = ("ButtonEmbedView", "ExtendedEmbed", "Field")

P = ParamSpec("P")


class ButtonEmbedView(View):
    """Base view including common buttons."""

    def __init__(
        self,
        author: int,
        bot: Bot,
        original_embed: Embed,
        minified_embed: Embed,
        *args,
        **kwargs,  # type: ignore[misc]
    ) -> None:
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

    async def delete_interaction_check(self, interaction: Interaction) -> bool:
        """Check if the user is the author or a guild admin.

        .. note:: Only checks for the ``delete`` button, as we want to expose
            the ``learn more`` button to anyone.

        Args:
            interaction: Interaction object.

        Returns:
            True if the user is the author or a guild admin, False otherwise.
        """
        if interaction.user.id == self.author_id or (
            getattr(interaction.user, "guild_permissions", None) and interaction.user.guild_permissions.administrator  # type: ignore[attr-defined]
        ):
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
        if await self.delete_interaction_check(interaction):
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


class Field(TypedDict):
    """Field type for ``ExtendedEmbed``.

    .. note:: types are matching the ones in ``Embed.add_fields``.
    """

    name: Any
    value: Any
    inline: NotRequired[bool]


class ExtendedEmbed(Embed):
    """Extended Embed class for discord.py."""

    def add_field_dict(self, field: Field) -> Self:
        """Add a field to the embed.

        Args:
            field (Field): The field to add to the embed.

        Returns:
            Self: The embed with the field added.
        """
        self.add_field(**field)
        return self

    def add_field_dicts(self, fields: list[Field]) -> Self:
        """Add multiple fields to the embed.

        Args:
            fields (list[Field]): A list of fields to add to the embed.

        Returns:
            Self: The embed with the fields added.
        """
        for field in fields:
            self.add_field_dict(field)
        return self

    @classmethod
    def from_field_dicts(
        cls,
        colour: int | Colour | None = None,
        color: int | Colour | None = None,
        title: Any | None = None,
        type: Literal["rich", "image", "video", "gifv", "article", "link"] = "rich",  # noqa: A002
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None,
        fields: list[Field] | None = None,
    ) -> Self:
        """Create an embed from a list of fields.

        Args:
            colour (int | Colour | None): The colour of the embed.
            color (int | Colour | None): The colour of the embed.
            title (Any | None): The title of the embed.
            type (Literal["rich", "image", "video", "gifv", "article", "link"]): The type of the embed.
            url (Any | None): The URL of the embed.
            description (Any | None): The description of the embed.
            timestamp (datetime | None): The timestamp of the embed.
            fields (list[Field] | None): A list of fields to add to the embed.

        Returns:
            Self: The embed with the fields added.
        """
        embed = cls(
            colour=colour,
            color=color,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )
        embed.add_field_dicts(fields or [])
        return embed

    def deepcopy(self) -> Self:
        """Create a deep copy of the embed.

        Returns:
            Self: A deep copy of the embed.
        """
        return deepcopy(self)
