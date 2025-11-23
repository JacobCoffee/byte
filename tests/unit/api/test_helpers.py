"""Tests for domain helper functions."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest

from byte_api.domain.guilds.helpers import get_byte_server_count
from byte_api.domain.system.helpers import check_byte_status, check_database_status

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = [
    "TestByteStatusHelper",
    "TestDatabaseStatusHelper",
    "TestGuildHelpers",
]


@pytest.mark.asyncio
class TestDatabaseStatusHelper:
    """Tests for check_database_status helper."""

    async def test_check_database_status_online(self, db_session: AsyncSession) -> None:
        """Test database status returns online when healthy."""
        status = await check_database_status(db_session)

        # With a working test database, should be online
        assert status in ["online", "degraded"]

    async def test_check_database_status_degraded_slow_response(self) -> None:
        """Test database status returns degraded when response is slow."""
        # Mock a slow database response
        mock_session = AsyncMock()

        # Simulate slow response by patching time
        with patch("byte_api.domain.system.helpers.time") as mock_time:
            # First call (start_time) = 0, second call (end_time) = 3.0
            mock_time.side_effect = [0.0, 3.0]

            status = await check_database_status(mock_session)

            # Response time > DEGRADED_THRESHOLD (2.0)
            assert status == "degraded"

    async def test_check_database_status_offline_connection_refused(self) -> None:
        """Test database status returns offline on connection error."""
        mock_session = AsyncMock()
        mock_session.execute.side_effect = ConnectionRefusedError("Connection refused")

        status = await check_database_status(mock_session)

        assert status == "offline"


@pytest.mark.asyncio
class TestByteStatusHelper:
    """Tests for check_byte_status helper."""

    async def test_check_byte_status_returns_offline(self) -> None:
        """Test byte status returns offline (stub implementation)."""
        status = await check_byte_status()

        # Current implementation is a stub that returns "offline"
        assert status == "offline"


class TestGuildHelpers:
    """Tests for guild helper functions."""

    def test_get_byte_server_count_function_exists(self) -> None:
        """Test get_byte_server_count function is importable."""
        # Verify function exists and is callable
        assert callable(get_byte_server_count)

        # Note: Full integration testing of this function requires
        # a database connection, which is tested in integration tests
