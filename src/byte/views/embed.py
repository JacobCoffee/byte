from copy import deepcopy
from datetime import datetime
from typing import Any, Literal, Self, TypedDict

from discord import Colour, Embed

__all__ = ("ExtendedEmbed", "Field")


# TODO: find a better place


class Field(TypedDict):
    # NOTE: types are matching the ones in ``Embed`.add_fields`
    name: Any
    value: Any
    inline: bool = True


class ExtendedEmbed(Embed):
    # TODO: better name
    def add_field_dict(self, field: Field) -> Self:
        self.add_field(**field)
        return self

    def add_field_dicts(self, fields: list[Field]) -> Self:
        for field in fields:
            self.add_field_dict(field)
        return self

    @classmethod
    def from_field_dicts(
        cls,
        colour: int | Colour | None = None,
        color: int | Colour | None = None,
        title: Any | None = None,
        type: Literal["rich", "image", "video", "gifv", "article", "link"] = "rich",
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None,
        fields: list[Field] | None = None,
    ) -> Self:
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
        return deepcopy(self)
