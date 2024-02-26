"""DTO Library layer module."""
from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.dto import DataclassDTO, dto_field
from litestar.dto.config import DTOConfig

if TYPE_CHECKING:
    from collections.abc import Set as AbstractSet

    from litestar.dto import RenameStrategy

__all__ = ["config", "dto_field", "DTOConfig", "SQLAlchemyDTO", "DataclassDTO"]


@overload
def config(
    backend: Literal["sqlalchemy"] = "sqlalchemy",
    exclude: AbstractSet[str] | None = None,
    rename_fields: dict[str, str] | None = None,
    rename_strategy: RenameStrategy | None = None,
    max_nested_depth: int | None = None,
    partial: bool | None = None,
) -> SQLAlchemyDTOConfig:
    ...


@overload
def config(
    backend: Literal["dataclass"] = "dataclass",
    exclude: AbstractSet[str] | None = None,
    rename_fields: dict[str, str] | None = None,
    rename_strategy: RenameStrategy | None = None,
    max_nested_depth: int | None = None,
    partial: bool | None = None,
) -> DTOConfig:
    ...


# noinspection PyUnusedLocal
def config(
    backend: Literal["dataclass", "sqlalchemy"] = "dataclass",  # noqa: ARG001
    exclude: AbstractSet[str] | None = None,
    rename_fields: dict[str, str] | None = None,
    rename_strategy: RenameStrategy | None = None,
    max_nested_depth: int | None = None,
    partial: bool | None = None,
) -> DTOConfig | SQLAlchemyDTOConfig:
    """Construct a DTO config.

    Args:
        backend (Literal["dataclass", "sqlalchemy"], optional): Backend to use. Defaults to "dataclass".
        exclude (AbstractSet[str] | None, optional): Fields to exclude. Defaults to None.
        rename_fields (dict[str, str] | None, optional): Fields to rename. Defaults to None.
        rename_strategy (RenameStrategy | None, optional): Rename strategy to use. Defaults to None.
        max_nested_depth (int | None, optional): Max nested depth. Defaults to None.
        partial (bool | None, optional): Whether to make the DTO partial. Defaults to None.

    Returns:
        DTOConfig: Configured DTO class
    """
    default_kwargs = {"rename_strategy": "camel", "max_nested_depth": 2}
    if exclude:
        default_kwargs["exclude"] = exclude
    if rename_fields:
        default_kwargs["rename_fields"] = rename_fields
    if rename_strategy:
        default_kwargs["rename_strategy"] = rename_strategy
    if max_nested_depth:
        default_kwargs["max_nested_depth"] = max_nested_depth
    if partial:
        default_kwargs["partial"] = partial
    return DTOConfig(**default_kwargs)  # type: ignore[arg-type]
