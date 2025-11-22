"""Database settings base class."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ("DatabaseSettings",)


class DatabaseSettings(BaseSettings):
    """Database configuration base class.

    Services can inherit from this class to add service-specific database settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DB_",
        case_sensitive=False,
        extra="ignore",
    )

    ECHO: bool = False
    """Enable SQLAlchemy engine logs."""
    ECHO_POOL: bool | Literal["debug"] = False
    """Enable SQLAlchemy connection pool logs."""
    POOL_DISABLE: bool = True
    """Disable SQLAlchemy pooling.

    When True, uses NullPool which creates a new connection for each request.
    Useful in serverless environments or during development.
    """
    POOL_MAX_OVERFLOW: int = 10
    """Maximum number of connections to allow in connection pool overflow.

    See :class:`QueuePool <sqlalchemy.pool.QueuePool>`.
    """
    POOL_SIZE: int = 5
    """The size of the database connection pool.

    See :class:`QueuePool <sqlalchemy.pool.QueuePool>`.
    """
    POOL_TIMEOUT: int = 30
    """Seconds to wait before giving up on getting a connection from the pool.

    See :class:`QueuePool <sqlalchemy.pool.QueuePool>`.
    """
    POOL_RECYCLE: int = 300
    """Number of seconds after which to recycle connections.

    See :class:`QueuePool <sqlalchemy.pool.QueuePool>`.
    """
    POOL_PRE_PING: bool = False
    """Enable connection health checks before checkout.

    See :class:`QueuePool <sqlalchemy.pool.QueuePool>`.
    """
    CONNECT_ARGS: dict[str, Any] = Field(default_factory=dict)
    """Connection arguments to pass to the database driver."""
    URL: str = "postgresql+asyncpg://byte:bot@localhost:5432/byte"
    """Database connection URL."""
    ENGINE: str | None = None
    """Database engine identifier."""
    USER: str = "byte"
    """Database user."""
    PASSWORD: str = "bot"  # noqa: S105
    """Database password."""
    HOST: str = "localhost"
    """Database host."""
    PORT: int = 5432
    """Database port."""
    NAME: str = "byte"
    """Database name."""
