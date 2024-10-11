"""Custom embed view with convenience methods."""

from copy import deepcopy
from datetime import datetime
from typing import Any, Literal, Self, TypedDict

from discord import Colour, Embed

__all__ = ("ExtendedEmbed", "Field")


class Field(TypedDict):
    """Field type for ``ExtendedEmbed``.

    .. note:: types are matching the ones in ``Embed.add_fields``.
    """

    name: Any
    value: Any
    inline: bool


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
