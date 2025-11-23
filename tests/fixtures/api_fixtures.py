"""API test fixtures for Litestar testing."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from litestar import Litestar
from litestar.testing import AsyncTestClient

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

__all__ = [
    "api_app",
    "api_client",
    "mock_db_session",
]


@pytest.fixture
async def api_app(async_session: async_sessionmaker[AsyncSession]) -> Litestar:
    """Create Litestar app with test database.

    This fixture creates a Litestar application configured to use
    the in-memory test database instead of the production database.

    Args:
        async_session: Test database session factory from conftest.

    Returns:
        Configured Litestar application for testing.
    """
    from byte_api.app import create_app

    # Create app with default config (will be overridden by dependency injection)
    return create_app()


@pytest.fixture
async def api_client(
    api_app: Litestar,
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncTestClient[Litestar]]:
    """Create async test client with test database.

    This fixture provides an AsyncTestClient for making HTTP requests
    to the API endpoints. The client is configured with a test database
    session that uses SQLite in-memory for isolation.

    Args:
        api_app: Litestar application instance.
        db_session: Test database session.

    Yields:
        Configured AsyncTestClient for making API requests.
    """
    # Override the db_session dependency with our test session
    async with AsyncTestClient(app=api_app) as client:
        # Store the test session for dependency injection
        client.app.state.session = db_session
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
