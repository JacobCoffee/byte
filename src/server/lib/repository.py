"""Repository module."""
from __future__ import annotations

import random
import string
from typing import TYPE_CHECKING, Any, Protocol

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.repository.typing import ModelT
from litestar.repository.handlers import on_app_init as _on_app_init

from src.utils import slugify

if TYPE_CHECKING:
    from litestar.config.app import AppConfig
    from sqlalchemy import Select, StatementLambdaElement

__all__ = ["SQLAlchemyAsyncRepository", "SQLAlchemyAsyncSlugRepository", "on_app_init"]


def on_app_init(app_config: AppConfig) -> AppConfig:
    """Executes on application init.  Injects signature namespaces."""
    app_config.signature_namespace.update(
        {
            "SQLAlchemyAsyncSlugRepository": SQLAlchemyAsyncSlugRepository,
            "SQLAlchemyAsyncRepository": SQLAlchemyAsyncRepository,
        },
    )
    return _on_app_init(app_config)


class FieldSearchProtocol(Protocol):
    """Protocol for adding search by field capabilities to a repository."""

    async def get_one_or_none(
        self,
        auto_expunge: bool | None = None,
        statement: Select[tuple[ModelT]] | StatementLambdaElement | None = None,
        **kwargs: Any,
    ) -> ModelT | None:
        """Select a single record.

        Matches `advanced_alchemy.repository._async.SQLAlchemyAsyncRepository.get_one_or_none`
        """
        ...


class SQLAlchemyAsyncSlugRepository(SQLAlchemyAsyncRepository[ModelT]):
    """Extends the repository to include slug model features."""

    async def get_by_slug(
        self,
        slug: str,
        **kwargs: Any,  # noqa: ARG002
    ) -> ModelT | None:
        """Select record by slug value.

        Args:
            slug (str): slug value
            **kwargs: Keyword arguments

        Returns:
            ModelT | None: Model record
        """
        return await self.get_one_or_none(slug=slug)

    async def get_available_slug(
        self,
        value_to_slugify: str,
        **kwargs: Any,  # noqa: ARG002
    ) -> str:
        """Get a unique slug for the supplied value.

        If the value is found to exist, a random 4-digit character is appended to the end.
        There may be a better way to do this, but I wanted to limit the number of additional database calls.

        Args:
            value_to_slugify (str): A string that should be converted to a unique slug.
            **kwargs: Keyword arguments

        Returns:
            str: a unique slug for the supplied value.
                This is safe for URLs and other unique identifiers.
        """
        slug = slugify(value_to_slugify)
        if await self._is_slug_unique(slug):
            return slug
        random_string = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))  # noqa: S311
        return f"{slug}-{random_string}"

    async def _is_slug_unique(
        self,
        slug: str,
        **kwargs: Any,  # noqa: ARG002
    ) -> bool:
        return await self.get_one_or_none(slug=slug) is None
