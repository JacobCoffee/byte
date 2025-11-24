"""Tests for ByteAPIClient retry logic and statistics."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
import respx
from httpx import ConnectError, ConnectTimeout, ReadTimeout, Response

from byte_bot.api_client import APIError, ByteAPIClient
from byte_common.schemas.guild import GuildSchema

if TYPE_CHECKING:
    from respx import MockRouter


class TestRetryLogic:
    """Tests for retry logic with exponential backoff."""

    @respx.mock
    async def test_create_guild_retries_on_500_error(self, respx_mock: MockRouter) -> None:
        """Test that create_guild retries on 5xx errors."""
        guild_data = {
            "id": str(uuid4()),
            "guild_id": 123456789,
            "guild_name": "Test Guild",
            "prefix": "!",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        # First 2 attempts fail with 500, 3rd succeeds
        route = respx_mock.post("http://localhost:8000/api/guilds")
        route.side_effect = [
            Response(500, json={"detail": "Internal server error"}),
            Response(500, json={"detail": "Internal server error"}),
            Response(201, json=guild_data),
        ]

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

        assert isinstance(result, GuildSchema)
        assert result.guild_id == 123456789
        assert route.call_count == 3
        assert client.retry_stats["total_retries"] == 2
        assert client.retry_stats["retried_methods"]["create_guild"] == 2

    @respx.mock
    async def test_create_guild_no_retry_on_400_error(self, respx_mock: MockRouter) -> None:
        """Test that create_guild does NOT retry on 4xx errors."""
        route = respx_mock.post("http://localhost:8000/api/guilds")
        route.mock(return_value=Response(400, json={"detail": "Bad request"}))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

        assert exc_info.value.status_code == 400
        assert route.call_count == 1  # Should NOT retry
        assert client.retry_stats["total_retries"] == 0
        assert client.retry_stats["failed_requests"] == 1

    @respx.mock
    async def test_create_guild_retries_on_connection_error(self, respx_mock: MockRouter) -> None:
        """Test that create_guild retries on connection errors."""
        guild_data = {
            "id": str(uuid4()),
            "guild_id": 123456789,
            "guild_name": "Test Guild",
            "prefix": "!",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        # First 2 attempts fail with connection error, 3rd succeeds
        route = respx_mock.post("http://localhost:8000/api/guilds")
        route.side_effect = [
            ConnectError("Connection refused"),
            ConnectError("Connection refused"),
            Response(201, json=guild_data),
        ]

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

        assert isinstance(result, GuildSchema)
        assert route.call_count == 3
        assert client.retry_stats["total_retries"] == 2

    @respx.mock
    async def test_create_guild_max_retries_exceeded(self, respx_mock: MockRouter) -> None:
        """Test that create_guild fails after max retries."""
        route = respx_mock.post("http://localhost:8000/api/guilds")
        route.mock(return_value=Response(500, json={"detail": "Internal server error"}))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

        assert exc_info.value.status_code == 500
        assert route.call_count == 3  # Max 3 attempts
        assert client.retry_stats["total_retries"] == 3

    @respx.mock
    async def test_get_guild_retries_on_503_error(self, respx_mock: MockRouter) -> None:
        """Test that get_guild retries on 5xx errors."""
        guild_data = {
            "id": str(uuid4()),
            "guild_id": 123456789,
            "guild_name": "Test Guild",
            "prefix": "!",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        # First attempt fails with 503, 2nd succeeds
        route = respx_mock.get("http://localhost:8000/api/guilds/123456789")
        route.side_effect = [
            Response(503, json={"detail": "Service unavailable"}),
            Response(200, json=guild_data),
        ]

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.get_guild(guild_id=123456789)

        assert isinstance(result, GuildSchema)
        assert route.call_count == 2
        assert client.retry_stats["total_retries"] == 1
        assert client.retry_stats["retried_methods"]["get_guild"] == 1

    @respx.mock
    async def test_get_guild_no_retry_on_404(self, respx_mock: MockRouter) -> None:
        """Test that get_guild does NOT retry on 404 (returns None)."""
        route = respx_mock.get("http://localhost:8000/api/guilds/999999999")
        route.mock(return_value=Response(404, json={"detail": "Not found"}))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.get_guild(guild_id=999999999)

        assert result is None
        assert route.call_count == 1  # Should NOT retry
        assert client.retry_stats["total_retries"] == 0

    @respx.mock
    async def test_update_guild_retries_on_502_error(self, respx_mock: MockRouter) -> None:
        """Test that update_guild retries on 5xx errors."""
        guild_uuid = uuid4()
        updated_data = {
            "id": str(guild_uuid),
            "guild_id": 123456789,
            "guild_name": "Updated Guild",
            "prefix": ">>",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T13:00:00Z",
        }

        # First attempt fails with 502, 2nd succeeds
        route = respx_mock.patch(f"http://localhost:8000/api/guilds/{guild_uuid}")
        route.side_effect = [
            Response(502, json={"detail": "Bad gateway"}),
            Response(200, json=updated_data),
        ]

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.update_guild(guild_id=guild_uuid, prefix=">>")

        assert isinstance(result, GuildSchema)
        assert result.prefix == ">>"
        assert route.call_count == 2
        assert client.retry_stats["total_retries"] == 1

    @respx.mock
    async def test_delete_guild_retries_on_500_error(self, respx_mock: MockRouter) -> None:
        """Test that delete_guild retries on 5xx errors."""
        guild_uuid = uuid4()

        # First attempt fails with 500, 2nd succeeds
        route = respx_mock.delete(f"http://localhost:8000/api/guilds/{guild_uuid}")
        route.side_effect = [
            Response(500, json={"detail": "Internal server error"}),
            Response(204),
        ]

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            await client.delete_guild(guild_id=guild_uuid)

        assert route.call_count == 2
        assert client.retry_stats["total_retries"] == 1

    @respx.mock
    async def test_health_check_retries_on_connection_timeout(self, respx_mock: MockRouter) -> None:
        """Test that health_check retries on connection timeout."""
        health_data = {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T12:00:00Z",
        }

        # First attempt times out, 2nd succeeds
        route = respx_mock.get("http://localhost:8000/health")
        route.side_effect = [
            ConnectTimeout("Connection timeout"),
            Response(200, json=health_data),
        ]

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.health_check()

        assert result["status"] == "healthy"
        assert route.call_count == 2
        assert client.retry_stats["total_retries"] == 1

    @respx.mock
    async def test_health_check_retries_on_read_timeout(self, respx_mock: MockRouter) -> None:
        """Test that health_check retries on read timeout."""
        health_data = {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T12:00:00Z",
        }

        # First attempt times out, 2nd succeeds
        route = respx_mock.get("http://localhost:8000/health")
        route.side_effect = [
            ReadTimeout("Read timeout"),
            Response(200, json=health_data),
        ]

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.health_check()

        assert result["status"] == "healthy"
        assert route.call_count == 2
        assert client.retry_stats["total_retries"] == 1


class TestRetryStatistics:
    """Tests for retry statistics tracking."""

    @respx.mock
    async def test_retry_stats_initialized_correctly(self, respx_mock: MockRouter) -> None:
        """Test that retry stats are initialized with correct default values."""
        client = ByteAPIClient(base_url="http://localhost:8000")
        assert client.retry_stats["total_retries"] == 0
        assert client.retry_stats["failed_requests"] == 0
        assert client.retry_stats["retried_methods"] == {}

    @respx.mock
    async def test_retry_stats_track_multiple_methods(self, respx_mock: MockRouter) -> None:
        """Test that retry stats track retries across multiple methods."""
        guild_data = {
            "id": str(uuid4()),
            "guild_id": 123456789,
            "guild_name": "Test Guild",
            "prefix": "!",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        # Mock create_guild to fail once then succeed
        create_route = respx_mock.post("http://localhost:8000/api/guilds")
        create_route.side_effect = [
            Response(500, json={"detail": "Internal server error"}),
            Response(201, json=guild_data),
        ]

        # Mock get_guild to fail twice then succeed
        get_route = respx_mock.get("http://localhost:8000/api/guilds/123456789")
        get_route.side_effect = [
            Response(500, json={"detail": "Internal server error"}),
            Response(500, json={"detail": "Internal server error"}),
            Response(200, json=guild_data),
        ]

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            # Call create_guild (1 retry)
            await client.create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

            # Call get_guild (2 retries)
            await client.get_guild(guild_id=123456789)

        assert client.retry_stats["total_retries"] == 3
        assert client.retry_stats["retried_methods"]["create_guild"] == 1
        assert client.retry_stats["retried_methods"]["get_guild"] == 2

    @respx.mock
    async def test_failed_requests_tracked_separately(self, respx_mock: MockRouter) -> None:
        """Test that failed requests (4xx) are tracked separately from retries."""
        # Mock 400 error (should not retry)
        route1 = respx_mock.post("http://localhost:8000/api/guilds")
        route1.mock(return_value=Response(400, json={"detail": "Bad request"}))

        # Mock 404 error (should not retry)
        route2 = respx_mock.get("http://localhost:8000/api/guilds/999999999")
        route2.mock(return_value=Response(404, json={"detail": "Not found"}))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            # Call create_guild (400 error - no retry)
            with pytest.raises(APIError):
                await client.create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

            # Call get_guild (404 - no retry, returns None)
            result = await client.get_guild(guild_id=999999999)

        assert result is None
        assert client.retry_stats["total_retries"] == 0
        assert client.retry_stats["failed_requests"] == 1  # Only 400 counts as failure


class TestExponentialBackoff:
    """Tests for exponential backoff timing."""

    @respx.mock
    async def test_exponential_backoff_timing(self, respx_mock: MockRouter) -> None:
        """Test that exponential backoff increases wait time between retries."""
        import time

        guild_data = {
            "id": str(uuid4()),
            "guild_id": 123456789,
            "guild_name": "Test Guild",
            "prefix": "!",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        # First 2 attempts fail, 3rd succeeds
        route = respx_mock.post("http://localhost:8000/api/guilds")
        route.side_effect = [
            Response(500, json={"detail": "Internal server error"}),
            Response(500, json={"detail": "Internal server error"}),
            Response(201, json=guild_data),
        ]

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            start_time = time.time()
            result = await client.create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")
            elapsed = time.time() - start_time

        assert isinstance(result, GuildSchema)
        # Should take at least 1s (first retry) + 2s (second retry) = 3s
        # But not more than 5s (accounting for overhead)
        assert 2.5 < elapsed < 5.0, f"Expected 2.5-5.0s, got {elapsed:.2f}s"

    @respx.mock
    async def test_successful_request_no_delay(self, respx_mock: MockRouter) -> None:
        """Test that successful requests have no retry delay."""
        import time

        guild_data = {
            "id": str(uuid4()),
            "guild_id": 123456789,
            "guild_name": "Test Guild",
            "prefix": "!",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        route = respx_mock.post("http://localhost:8000/api/guilds")
        route.mock(return_value=Response(201, json=guild_data))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            start_time = time.time()
            result = await client.create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")
            elapsed = time.time() - start_time

        assert isinstance(result, GuildSchema)
        # Should complete quickly (< 1s) with no retries
        assert elapsed < 1.0, f"Expected < 1.0s, got {elapsed:.2f}s"
        assert client.retry_stats["total_retries"] == 0


class TestGetOrCreateGuildRetry:
    """Tests for get_or_create_guild retry behavior (composite method)."""

    @respx.mock
    async def test_get_or_create_retries_on_get_failure(self, respx_mock: MockRouter) -> None:
        """Test that get_or_create retries when get_guild fails with 5xx."""
        guild_data = {
            "id": str(uuid4()),
            "guild_id": 123456789,
            "guild_name": "Test Guild",
            "prefix": "!",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        # get_guild fails once with 500, then returns 404
        get_route = respx_mock.get("http://localhost:8000/api/guilds/123456789")
        get_route.side_effect = [
            Response(500, json={"detail": "Internal server error"}),
            Response(404, json={"detail": "Not found"}),
        ]

        # create_guild succeeds
        create_route = respx_mock.post("http://localhost:8000/api/guilds")
        create_route.mock(return_value=Response(201, json=guild_data))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.get_or_create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

        assert isinstance(result, GuildSchema)
        assert get_route.call_count == 2
        assert create_route.call_count == 1
        assert client.retry_stats["total_retries"] == 1
        assert client.retry_stats["retried_methods"]["get_guild"] == 1

    @respx.mock
    async def test_get_or_create_retries_on_create_failure(self, respx_mock: MockRouter) -> None:
        """Test that get_or_create retries when create_guild fails with 5xx."""
        guild_data = {
            "id": str(uuid4()),
            "guild_id": 123456789,
            "guild_name": "Test Guild",
            "prefix": "!",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        # get_guild returns 404
        get_route = respx_mock.get("http://localhost:8000/api/guilds/123456789")
        get_route.mock(return_value=Response(404, json={"detail": "Not found"}))

        # create_guild fails once with 500, then succeeds
        create_route = respx_mock.post("http://localhost:8000/api/guilds")
        create_route.side_effect = [
            Response(500, json={"detail": "Internal server error"}),
            Response(201, json=guild_data),
        ]

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.get_or_create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

        assert isinstance(result, GuildSchema)
        assert get_route.call_count == 1
        assert create_route.call_count == 2
        assert client.retry_stats["total_retries"] == 1
        assert client.retry_stats["retried_methods"]["create_guild"] == 1
