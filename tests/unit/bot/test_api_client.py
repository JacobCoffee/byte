"""Tests for ByteAPIClient."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
import respx
from httpx import ConnectError, Response, TimeoutException

from byte_bot.api_client import APIError, ByteAPIClient
from byte_common.schemas.guild import GuildSchema

if TYPE_CHECKING:
    from respx import MockRouter


class TestAPIError:
    """Tests for APIError exception."""

    def test_api_error_with_status_code(self) -> None:
        """Test APIError initialization with status code."""
        error = APIError("Test error", status_code=400)
        assert str(error) == "Test error"
        assert error.status_code == 400

    def test_api_error_without_status_code(self) -> None:
        """Test APIError initialization without status code."""
        error = APIError("Test error")
        assert str(error) == "Test error"
        assert error.status_code is None


class TestByteAPIClientInitialization:
    """Tests for ByteAPIClient initialization and context manager."""

    def test_client_initialization(self) -> None:
        """Test client initializes with correct base URL and timeout."""
        client = ByteAPIClient(base_url="http://localhost:8000", timeout=10.0)
        assert client.base_url == "http://localhost:8000"
        assert client.client.timeout.read == 10.0

    def test_client_strips_trailing_slash(self) -> None:
        """Test client strips trailing slash from base URL."""
        client = ByteAPIClient(base_url="http://localhost:8000/", timeout=10.0)
        assert client.base_url == "http://localhost:8000"

    def test_client_default_timeout(self) -> None:
        """Test client uses default timeout."""
        client = ByteAPIClient(base_url="http://localhost:8000")
        assert client.client.timeout.read == 10.0

    def test_client_headers(self) -> None:
        """Test client sets correct headers."""
        client = ByteAPIClient(base_url="http://localhost:8000")
        assert client.client.headers["Content-Type"] == "application/json"

    async def test_context_manager(self) -> None:
        """Test client works as async context manager."""
        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            assert isinstance(client, ByteAPIClient)

    async def test_close(self) -> None:
        """Test client close method."""
        client = ByteAPIClient(base_url="http://localhost:8000")
        await client.close()
        # Verify client is closed by checking it can't make requests
        assert client.client.is_closed


class TestCreateGuild:
    """Tests for create_guild method."""

    @respx.mock
    async def test_create_guild_success(self, respx_mock: MockRouter) -> None:
        """Test successful guild creation."""
        guild_data = {
            "id": str(uuid4()),
            "guild_id": 123456789,
            "guild_name": "Test Guild",
            "prefix": "!",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        respx_mock.post("http://localhost:8000/api/guilds").mock(return_value=Response(201, json=guild_data))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

        assert isinstance(result, GuildSchema)
        assert result.guild_id == 123456789
        assert result.guild_name == "Test Guild"
        assert result.prefix == "!"

    @respx.mock
    async def test_create_guild_with_kwargs(self, respx_mock: MockRouter) -> None:
        """Test guild creation with additional kwargs."""
        guild_data = {
            "id": str(uuid4()),
            "guild_id": 123456789,
            "guild_name": "Test Guild",
            "prefix": ">>",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        respx_mock.post("http://localhost:8000/api/guilds").mock(return_value=Response(201, json=guild_data))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.create_guild(guild_id=123456789, guild_name="Test Guild", prefix=">>")

        assert result.prefix == ">>"

    @respx.mock
    async def test_create_guild_api_validation_error(self, respx_mock: MockRouter) -> None:
        """Test guild creation with API-level validation error (400)."""
        error_response = {"detail": "Guild already exists"}

        respx_mock.post("http://localhost:8000/api/guilds").mock(return_value=Response(400, json=error_response))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.create_guild(guild_id=123456789, guild_name="Duplicate Guild", prefix="!")

        assert exc_info.value.status_code == 400
        assert "Failed to create guild" in str(exc_info.value)

    @respx.mock
    async def test_create_guild_server_error(self, respx_mock: MockRouter) -> None:
        """Test guild creation with server error (500)."""
        respx_mock.post("http://localhost:8000/api/guilds").mock(
            return_value=Response(500, json={"detail": "Internal server error"})
        )

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

        assert exc_info.value.status_code == 500

    @respx.mock
    async def test_create_guild_connection_error(self, respx_mock: MockRouter) -> None:
        """Test guild creation with connection error."""
        respx_mock.post("http://localhost:8000/api/guilds").mock(side_effect=ConnectError("Connection refused"))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

        assert "Failed to connect to API service" in str(exc_info.value)
        assert exc_info.value.status_code is None

    @respx.mock
    async def test_create_guild_timeout(self, respx_mock: MockRouter) -> None:
        """Test guild creation with timeout."""
        respx_mock.post("http://localhost:8000/api/guilds").mock(side_effect=TimeoutException("Timeout"))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

        assert "Failed to connect to API service" in str(exc_info.value)


class TestGetGuild:
    """Tests for get_guild method."""

    @respx.mock
    async def test_get_guild_success(self, respx_mock: MockRouter) -> None:
        """Test successful guild retrieval."""
        guild_data = {
            "id": str(uuid4()),
            "guild_id": 123456789,
            "guild_name": "Test Guild",
            "prefix": "!",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        respx_mock.get("http://localhost:8000/api/guilds/123456789").mock(return_value=Response(200, json=guild_data))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.get_guild(guild_id=123456789)

        assert isinstance(result, GuildSchema)
        assert result.guild_id == 123456789
        assert result.guild_name == "Test Guild"

    @respx.mock
    async def test_get_guild_not_found(self, respx_mock: MockRouter) -> None:
        """Test guild retrieval returns None for 404."""
        respx_mock.get("http://localhost:8000/api/guilds/999999999").mock(
            return_value=Response(404, json={"detail": "Not found"})
        )

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.get_guild(guild_id=999999999)

        assert result is None

    @respx.mock
    async def test_get_guild_server_error(self, respx_mock: MockRouter) -> None:
        """Test guild retrieval with server error."""
        respx_mock.get("http://localhost:8000/api/guilds/123456789").mock(
            return_value=Response(500, json={"detail": "Internal server error"})
        )

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.get_guild(guild_id=123456789)

        assert exc_info.value.status_code == 500
        assert "Failed to get guild" in str(exc_info.value)

    @respx.mock
    async def test_get_guild_connection_error(self, respx_mock: MockRouter) -> None:
        """Test guild retrieval with connection error."""
        respx_mock.get("http://localhost:8000/api/guilds/123456789").mock(
            side_effect=ConnectError("Connection refused")
        )

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.get_guild(guild_id=123456789)

        assert "Failed to connect to API service" in str(exc_info.value)


class TestUpdateGuild:
    """Tests for update_guild method."""

    @respx.mock
    async def test_update_guild_success(self, respx_mock: MockRouter) -> None:
        """Test successful guild update."""
        guild_uuid = uuid4()
        updated_data = {
            "id": str(guild_uuid),
            "guild_id": 123456789,
            "guild_name": "Updated Guild",
            "prefix": ">>",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T13:00:00Z",
        }

        respx_mock.patch(f"http://localhost:8000/api/guilds/{guild_uuid}").mock(
            return_value=Response(200, json=updated_data)
        )

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.update_guild(guild_id=guild_uuid, prefix=">>")

        assert isinstance(result, GuildSchema)
        assert result.prefix == ">>"
        assert result.guild_name == "Updated Guild"

    @respx.mock
    async def test_update_guild_partial(self, respx_mock: MockRouter) -> None:
        """Test partial guild update."""
        guild_uuid = uuid4()
        updated_data = {
            "id": str(guild_uuid),
            "guild_id": 123456789,
            "guild_name": "Test Guild",
            "prefix": "?",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T13:00:00Z",
        }

        respx_mock.patch(f"http://localhost:8000/api/guilds/{guild_uuid}").mock(
            return_value=Response(200, json=updated_data)
        )

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.update_guild(guild_id=guild_uuid, prefix="?")

        assert result.prefix == "?"

    @respx.mock
    async def test_update_guild_not_found(self, respx_mock: MockRouter) -> None:
        """Test update with non-existent guild."""
        guild_uuid = uuid4()
        respx_mock.patch(f"http://localhost:8000/api/guilds/{guild_uuid}").mock(
            return_value=Response(404, json={"detail": "Not found"})
        )

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.update_guild(guild_id=guild_uuid, prefix=">>")

        assert exc_info.value.status_code == 404

    @respx.mock
    async def test_update_guild_api_error(self, respx_mock: MockRouter) -> None:
        """Test update with API-level error."""
        guild_uuid = uuid4()
        error_response = {"detail": "Invalid update"}

        respx_mock.patch(f"http://localhost:8000/api/guilds/{guild_uuid}").mock(
            return_value=Response(400, json=error_response)
        )

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.update_guild(guild_id=guild_uuid, prefix=">>")

        assert exc_info.value.status_code == 400
        assert "Failed to update guild" in str(exc_info.value)

    @respx.mock
    async def test_update_guild_connection_error(self, respx_mock: MockRouter) -> None:
        """Test update with connection error."""
        guild_uuid = uuid4()
        respx_mock.patch(f"http://localhost:8000/api/guilds/{guild_uuid}").mock(
            side_effect=ConnectError("Connection refused")
        )

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.update_guild(guild_id=guild_uuid, prefix=">>")

        assert "Failed to connect to API service" in str(exc_info.value)


class TestDeleteGuild:
    """Tests for delete_guild method."""

    @respx.mock
    async def test_delete_guild_success(self, respx_mock: MockRouter) -> None:
        """Test successful guild deletion."""
        guild_uuid = uuid4()
        respx_mock.delete(f"http://localhost:8000/api/guilds/{guild_uuid}").mock(return_value=Response(204))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            # Should not raise any exception
            await client.delete_guild(guild_id=guild_uuid)

    @respx.mock
    async def test_delete_guild_not_found(self, respx_mock: MockRouter) -> None:
        """Test delete with non-existent guild."""
        guild_uuid = uuid4()
        respx_mock.delete(f"http://localhost:8000/api/guilds/{guild_uuid}").mock(
            return_value=Response(404, json={"detail": "Not found"})
        )

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.delete_guild(guild_id=guild_uuid)

        assert exc_info.value.status_code == 404
        assert "Failed to delete guild" in str(exc_info.value)

    @respx.mock
    async def test_delete_guild_server_error(self, respx_mock: MockRouter) -> None:
        """Test delete with server error."""
        guild_uuid = uuid4()
        respx_mock.delete(f"http://localhost:8000/api/guilds/{guild_uuid}").mock(
            return_value=Response(500, json={"detail": "Internal server error"})
        )

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.delete_guild(guild_id=guild_uuid)

        assert exc_info.value.status_code == 500

    @respx.mock
    async def test_delete_guild_connection_error(self, respx_mock: MockRouter) -> None:
        """Test delete with connection error."""
        guild_uuid = uuid4()
        respx_mock.delete(f"http://localhost:8000/api/guilds/{guild_uuid}").mock(
            side_effect=ConnectError("Connection refused")
        )

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.delete_guild(guild_id=guild_uuid)

        assert "Failed to connect to API service" in str(exc_info.value)


class TestGetOrCreateGuild:
    """Tests for get_or_create_guild method."""

    @respx.mock
    async def test_get_or_create_returns_existing(self, respx_mock: MockRouter) -> None:
        """Test get_or_create returns existing guild."""
        guild_data = {
            "id": str(uuid4()),
            "guild_id": 123456789,
            "guild_name": "Existing Guild",
            "prefix": "!",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        # Mock GET to return existing guild
        respx_mock.get("http://localhost:8000/api/guilds/123456789").mock(return_value=Response(200, json=guild_data))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.get_or_create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

        assert isinstance(result, GuildSchema)
        assert result.guild_id == 123456789
        assert result.guild_name == "Existing Guild"

    @respx.mock
    async def test_get_or_create_creates_new(self, respx_mock: MockRouter) -> None:
        """Test get_or_create creates new guild if not found."""
        new_guild_data = {
            "id": str(uuid4()),
            "guild_id": 999999999,
            "guild_name": "New Guild",
            "prefix": ">>",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        # Mock GET to return 404
        respx_mock.get("http://localhost:8000/api/guilds/999999999").mock(
            return_value=Response(404, json={"detail": "Not found"})
        )

        # Mock POST to create new guild
        respx_mock.post("http://localhost:8000/api/guilds").mock(return_value=Response(201, json=new_guild_data))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.get_or_create_guild(guild_id=999999999, guild_name="New Guild", prefix=">>")

        assert isinstance(result, GuildSchema)
        assert result.guild_id == 999999999
        assert result.guild_name == "New Guild"
        assert result.prefix == ">>"

    @respx.mock
    async def test_get_or_create_idempotent(self, respx_mock: MockRouter) -> None:
        """Test get_or_create is idempotent."""
        guild_data = {
            "id": str(uuid4()),
            "guild_id": 123456789,
            "guild_name": "Test Guild",
            "prefix": "!",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
        }

        respx_mock.get("http://localhost:8000/api/guilds/123456789").mock(return_value=Response(200, json=guild_data))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result1 = await client.get_or_create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")
            result2 = await client.get_or_create_guild(guild_id=123456789, guild_name="Test Guild", prefix="!")

        assert result1.id == result2.id
        assert result1.guild_id == result2.guild_id


class TestHealthCheck:
    """Tests for health_check method."""

    @respx.mock
    async def test_health_check_success(self, respx_mock: MockRouter) -> None:
        """Test successful health check."""
        health_data = {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T12:00:00Z",
        }

        respx_mock.get("http://localhost:8000/health").mock(return_value=Response(200, json=health_data))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            result = await client.health_check()

        assert result["status"] == "healthy"
        assert result["database"] == "connected"

    @respx.mock
    async def test_health_check_unhealthy(self, respx_mock: MockRouter) -> None:
        """Test health check with unhealthy service."""
        respx_mock.get("http://localhost:8000/health").mock(return_value=Response(503, json={"status": "unhealthy"}))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.health_check()

        assert "API health check failed" in str(exc_info.value)

    @respx.mock
    async def test_health_check_connection_error(self, respx_mock: MockRouter) -> None:
        """Test health check with connection error."""
        respx_mock.get("http://localhost:8000/health").mock(side_effect=ConnectError("Connection refused"))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.health_check()

        assert "API health check failed" in str(exc_info.value)

    @respx.mock
    async def test_health_check_timeout(self, respx_mock: MockRouter) -> None:
        """Test health check with timeout."""
        respx_mock.get("http://localhost:8000/health").mock(side_effect=TimeoutException("Timeout"))

        async with ByteAPIClient(base_url="http://localhost:8000") as client:
            with pytest.raises(APIError) as exc_info:
                await client.health_check()

        assert "API health check failed" in str(exc_info.value)
