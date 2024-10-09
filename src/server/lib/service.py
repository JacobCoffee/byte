"""Service object implementation for SQLAlchemy.

RepositoryService object is generic on the domain model type, which
should be an SQLAlchemy model.
"""
from __future__ import annotations

import contextlib
from collections.abc import Sequence
from typing import TYPE_CHECKING, overload

from advanced_alchemy.filters import (
    FilterTypes,
    LimitOffset,
)
from advanced_alchemy.repository.typing import ModelT
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService as _SQLAlchemyAsyncRepositoryService
from litestar.pagination import OffsetPagination
from pydantic.type_adapter import TypeAdapter

from src.server.lib.db import async_session_factory

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from sqlalchemy import Select
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql import ColumnElement

    from src.server.lib.types import ModelDTOT, SQLAlchemyAsyncRepoServiceT

__all__ = ["SQLAlchemyAsyncRepositoryService"]


class SQLAlchemyAsyncRepositoryService(_SQLAlchemyAsyncRepositoryService[ModelT]):
    """Service object that operates on a repository object.

    This is the standard Advanced Alchemy Service with a few additional helper methods added:
        - Methods for formatting responses
        - Context manager for creating new services
    """

    @overload
    def to_dto(self, data: ModelT) -> ModelT:
        ...

    @overload
    def to_dto(
        self,
        data: Sequence[ModelT],
        total: int | None = None,
        *filters: FilterTypes | ColumnElement[bool],
    ) -> OffsetPagination[ModelT]:
        ...

    def to_dto(
        self,
        data: ModelT | Sequence[ModelT],
        total: int | None = None,
        *filters: FilterTypes | ColumnElement[bool],
    ) -> ModelT | OffsetPagination[ModelT]:
        """Convert the object to a format expected by the DTO handler.

        Args:
            data: The return from one of the service calls.
            total: the total number of rows in the data
            *filters: Collection route filters.

        Returns:
            The list of instances retrieved from the repository.
        """
        if not isinstance(data, Sequence | list):
            return data
        limit_offset = self.find_filter(LimitOffset, *filters)
        total = total or len(data)
        limit_offset = limit_offset if limit_offset is not None else LimitOffset(limit=len(data), offset=0)
        return OffsetPagination(
            items=list(data),
            limit=limit_offset.limit,
            offset=limit_offset.offset,
            total=total,
        )

    @overload
    def to_schema(self, dto: type[ModelDTOT], data: ModelT) -> ModelDTOT:
        ...

    @overload
    def to_schema(
        self,
        dto: type[ModelDTOT],
        data: Sequence[ModelT],
        total: int | None = None,
        *filters: FilterTypes,
    ) -> OffsetPagination[ModelDTOT]:
        ...

    def to_schema(
        self,
        dto: type[ModelDTOT],
        data: ModelT | Sequence[ModelT],
        total: int | None = None,
        *filters: FilterTypes,
    ) -> ModelDTOT | OffsetPagination[ModelDTOT]:
        """Convert the object to a response schema.

        Args:
            dto: Collection route filters.
            data: The return from one of the service calls.
            total: the total number of rows in the data
            *filters: Collection route filters.

        Returns:
            The list of instances retrieved from the repository.
        """
        if not isinstance(data, Sequence | list):
            return TypeAdapter(dto).validate_python(data)
        limit_offset = self.find_filter(LimitOffset, *filters)
        total = total or len(data)
        limit_offset = limit_offset if limit_offset is not None else LimitOffset(limit=len(data), offset=0)
        return OffsetPagination[dto](  # type: ignore[valid-type]
            items=TypeAdapter(list[dto]).validate_python(data),  # type: ignore[valid-type]
            limit=limit_offset.limit,
            offset=limit_offset.offset,
            total=total,
        )

    @classmethod
    @contextlib.asynccontextmanager
    async def new(
        cls: type[SQLAlchemyAsyncRepoServiceT],
        session: AsyncSession | None = None,
        statement: Select | None = None,
    ) -> AsyncIterator[SQLAlchemyAsyncRepoServiceT]:
        """Context manager that returns instance of service object.

        Handles construction of the database session._create_select_for_model

        Returns:
            The service object instance.
        """
        if session:
            yield cls(statement=statement, session=session)
        else:
            async with async_session_factory() as db_session:
                yield cls(
                    statement=statement,
                    session=db_session,
                )
