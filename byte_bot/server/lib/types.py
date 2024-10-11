"""Library module for type definitions to be used in the application."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypeAlias, TypeVar

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from advanced_alchemy.filters import FilterTypes
from litestar.dto import DataclassDTO, DTOData
from litestar.types import DataclassProtocol
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
    from pydantic import BaseModel

# -- Database Types
SQLAlchemyModelT = TypeVar("SQLAlchemyModelT", bound=DeclarativeBase)
"""Type variable for SQLAlchemy models."""
SQLAlchemyAsyncRepoServiceT = TypeVar("SQLAlchemyAsyncRepoServiceT", bound="SQLAlchemyAsyncRepositoryService")
"""Type variable for SQLAlchemy async repository services."""
DataclassModelT = TypeVar("DataclassModelT", bound=DataclassProtocol)
"""Type variable for dataclass models."""
ModelT: TypeAlias = SQLAlchemyModelT | DataclassModelT
"""Type alias for models."""
FilterTypeT = TypeVar("FilterTypeT", bound=FilterTypes)
"""Type variable for filter types."""

# -- DTO Types
ModelDTOT = TypeVar("ModelDTOT", bound="BaseModel")
"""Type variable for models."""
DTOT = TypeVar("DTOT", bound=DataclassProtocol | DeclarativeBase)
"""Type variable for DTOs."""
DTOFactoryT = TypeVar("DTOFactoryT", bound=DataclassDTO | SQLAlchemyDTO)
"""Type variable for DTO factories."""
ModelDictDTOT: TypeAlias = dict[str, Any] | ModelT | DTOData
"""Type alias for model or dict DTOs."""
ModelDictListDTOT: TypeAlias = list[ModelT | dict[str, Any]] | list[dict[str, Any]] | DTOData
"""Type alias for model or dict DTOs."""

# -- App Types
Status: TypeAlias = Literal["online", "offline", "degraded"]
"""Type alias for health check status."""
