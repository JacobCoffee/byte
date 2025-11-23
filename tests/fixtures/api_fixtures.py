"""API test fixtures for Litestar testing."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from litestar import Litestar
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = [
    "api_app",
    "api_client",
    "mock_db_session",
]


@pytest.fixture
async def api_app(async_engine: AsyncEngine) -> AsyncGenerator[Litestar]:
    """Create Litestar app with test database.

    This fixture creates a Litestar application configured to use
    the in-memory test database instead of the production database.

    The key challenge is that the production code registers PostgreSQL-specific
    event handlers that fail with SQLite. This fixture removes those handlers
    before creating the app.

    Args:
        async_engine: Test database engine from conftest.

    Returns:
        Configured Litestar application for testing.
    """
    import os
    from unittest.mock import patch

    from byte_api.app import create_app
    from byte_api.lib.db import base

    # Remove all event listeners from the sync engine to prevent PostgreSQL-specific
    # handlers from failing on SQLite connections
    if hasattr(base.engine.sync_engine, "dispatch"):
        base.engine.sync_engine.dispatch._clear()  # type: ignore[attr-defined]

    # Temporarily set environment to use test database and disable debug mode
    with patch.dict(os.environ, {"DB_URL": "sqlite+aiosqlite:///:memory:", "DEBUG": "false"}):
        # Replace the production engine and session factory with test versions
        original_engine = base.engine
        original_session_factory = base.async_session_factory

        base.engine = async_engine
        base.async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)

        # Update the config to use test engine
        base.config.engine_instance = async_engine
        base.config.session_maker = base.async_session_factory

        try:
            app = create_app()
            # Force debug mode off for tests to get proper JSON error responses
            app.debug = False
            yield app
        finally:
            # Restore original
            base.engine = original_engine
            base.async_session_factory = original_session_factory


@pytest.fixture
async def api_client(
    api_app: Litestar,
    async_session: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncTestClient[Litestar]]:
    """Create async test client with test database.

    This fixture provides an AsyncTestClient for making HTTP requests
    to the API endpoints. The client is configured with a test database
    session that uses SQLite in-memory for isolation.

    Args:
        api_app: Litestar application instance.
        async_session: Test database session factory.

    Yields:
        Configured AsyncTestClient for making API requests.
    """
    from litestar.di import Provide

    # Override the database session provider with test session factory
    async def provide_test_transaction() -> AsyncGenerator[AsyncSession]:
        """Provide test database session."""
        async with async_session() as session:
            async with session.begin():
                yield session

    # Replace the db_session dependency in the app
    api_app.dependencies["db_session"] = Provide(provide_test_transaction)

    async with AsyncTestClient(app=api_app) as client:
        yield client


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Create a mock database session for testing error conditions.

    This fixture is useful for testing error handling when database
    operations fail without actually connecting to a database.

    Returns:
        AsyncMock configured to simulate database session behavior.
    """
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session
