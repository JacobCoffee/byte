"""Database session and engine."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from advanced_alchemy.config import AlembicAsyncConfig
from advanced_alchemy.extensions.litestar.plugins.init.config import SQLAlchemyAsyncConfig
from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import autocommit_before_send_handler
from advanced_alchemy.extensions.litestar.plugins.init.plugin import SQLAlchemyInitPlugin
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from byte_bot.server.lib import constants, serialization, settings

__all__ = ["session", "engine", "async_session_factory", "config", "plugin"]

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from sqlalchemy.ext.asyncio import AsyncSession

engine = create_async_engine(
    settings.db.URL,
    future=True,
    json_serializer=serialization.to_json,
    json_deserializer=serialization.from_json,
    echo=settings.db.ECHO,
    echo_pool=True if settings.db.ECHO_POOL == "debug" else settings.db.ECHO_POOL,
    # max_overflow=settings.db.POOL_MAX_OVERFLOW,
    # pool_size=settings.db.POOL_SIZE,
    # pool_timeout=settings.db.POOL_TIMEOUT,
    pool_recycle=settings.db.POOL_RECYCLE,
    pool_pre_ping=settings.db.POOL_PRE_PING,
    # pool_use_lifo=True,
    poolclass=NullPool if settings.db.POOL_DISABLE else None,
    connect_args=settings.db.CONNECT_ARGS,
)
async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)
"""Database session factory.

See `async_sessionmaker <sqlalchemy.ext.asyncio.async_sessionmaker>`_.
"""


@event.listens_for(engine.sync_engine, "connect")
def _sqla_on_connect(dbapi_connection: Any, _: Any) -> Any:  # pragma: no cover
    """On connect event handler.

    Using msgspec for serialization of the json column values means that the
    output is binary, not ``str`` like ``json.dumps`` would output.
    SQLAlchemy expects that the json serializer returns ``str`` and calls ``.encode()`` on the value to
    turn it to bytes before writing to the JSONB column. I'd need to either wrap ``serialization.to_json`` to
    return a ``str`` so that SQLAlchemy could then convert it to binary, or do the following, which
    changes the behavior of the dialect to expect a binary value from the serializer.
    """

    def encoder(bin_value: bytes) -> bytes:
        return b"\x01" + serialization.to_json(bin_value)

    def decoder(bin_value: bytes) -> Any:
        # the byte is the \x01 prefix for jsonb used by PostgreSQL.
        # asyncpg returns it when format='binary'
        return serialization.from_json(bin_value[1:])

    dbapi_connection.await_(
        dbapi_connection.driver_connection.set_type_codec(
            "jsonb",
            encoder=encoder,
            decoder=decoder,
            schema="pg_catalog",
            format="binary",
        ),
    )
    dbapi_connection.await_(
        dbapi_connection.driver_connection.set_type_codec(
            "json",
            encoder=encoder,
            decoder=decoder,
            schema="pg_catalog",
            format="binary",
        ),
    )


config = SQLAlchemyAsyncConfig(
    session_dependency_key=constants.DB_SESSION_DEPENDENCY_KEY,
    engine_instance=engine,
    session_maker=async_session_factory,
    before_send_handler=autocommit_before_send_handler,
    alembic_config=AlembicAsyncConfig(
        version_table_name=settings.db.MIGRATION_DDL_VERSION_TABLE,
        script_config=settings.db.MIGRATION_CONFIG,
        script_location=settings.db.MIGRATION_PATH,
    ),
)

plugin = SQLAlchemyInitPlugin(config=config)


@asynccontextmanager
async def session() -> AsyncIterator[AsyncSession]:
    """Use this to get a database session where you can't in Litestar.

    .. deprecated:: Use :meth:`config.get_session <advanced_alchemy.config.asyncio.SQLAlchemyAsyncConfig.get_session>`
        instead. Introduced in `Advanced Alchemy v0.5.2 <https://github.com/jolt-org/advanced-alchemy/releases/tag/v0.5.2>`_.

    Returns:
        AsyncIterator[AsyncSession]
    """
    async with async_session_factory() as session:
        yield session
