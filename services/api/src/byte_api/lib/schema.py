"""Schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict

from byte_common.utils.strings import camel_case

__all__ = ["BaseModel", "CamelizedBaseModel", "serialize_camelized_model"]


class BaseModel(_BaseModel):
    """Base Settings."""

    model_config = ConfigDict(
        validate_assignment=True,
        from_attributes=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )


class CamelizedBaseModel(BaseModel):
    """Camelized Base pydantic schema.

    This model uses camelCase for field names in serialization by default.
    When serialized, snake_case fields will be converted to camelCase.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=camel_case,
    )


def serialize_camelized_model(value: Any) -> dict[str, Any]:
    """Serialize CamelizedBaseModel instances with camelCase field names.

    This encoder is used by Litestar to ensure that all Pydantic models
    extending CamelizedBaseModel are serialized with their aliases (camelCase).

    Args:
        value: The CamelizedBaseModel instance to serialize

    Returns:
        dict: The serialized model with camelCase field names
    """
    if isinstance(value, CamelizedBaseModel):
        return value.model_dump(by_alias=True, mode="json")
    return value
