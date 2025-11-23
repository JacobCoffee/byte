"""Application ORM configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from advanced_alchemy.base import UUIDAuditBase as TimestampedDatabaseModel
from advanced_alchemy.base import UUIDBase as DatabaseModel
from advanced_alchemy.base import orm_registry
from advanced_alchemy.mixins.audit import AuditColumns

if TYPE_CHECKING:
    from advanced_alchemy.repository.typing import ModelT
from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    declarative_mixin,
    mapped_column,
)

__all__ = ["AuditColumns", "DatabaseModel", "SlugKey", "TimestampedDatabaseModel", "model_from_dict", "orm_registry"]


@declarative_mixin
class SlugKey:
    """Slug unique Field Model Mixin."""

    __abstract__ = True
    slug: Mapped[str] = mapped_column(String(length=100), index=True, nullable=False, unique=True, sort_order=-9)


def model_from_dict(model: ModelT, **kwargs: Any) -> ModelT:
    """Return ORM Object from Dictionary."""
    data = {}
    for column in model.__table__.columns:
        column_val = kwargs.get(column.name, None)
        if column_val is not None:
            data[column.name] = column_val
    return model(**data)  # type: ignore[no-any-return, operator]
