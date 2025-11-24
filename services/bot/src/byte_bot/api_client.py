"""HTTP client for communicating with the Byte API service."""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Any, Self

import httpx

from byte_common.schemas.guild import CreateGuildRequest, GuildSchema, UpdateGuildRequest

if TYPE_CHECKING:
    from uuid import UUID

__all__ = ("APIError", "ByteAPIClient")

logger = logging.getLogger(__name__)

# HTTP status codes
HTTP_NOT_FOUND = 404


class APIError(Exception):
    """Exception raised when API calls fail."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code if available
        """
        super().__init__(message)
        self.status_code = status_code


class ByteAPIClient:
    """HTTP client for Byte API service.

    This client handles all communication between the bot service and the API service,
    replacing direct database access.
    """

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        """Initialize API client.

        Args:
            base_url: Base URL of the API service (e.g., "http://localhost:8000")
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        await self.close()

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make HTTP request with correlation ID tracking.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional httpx request parameters

        Returns:
            HTTP response

        Note:
            Automatically generates and logs correlation IDs for request tracing.
        """
        correlation_id = str(uuid.uuid4())
        headers = kwargs.pop("headers", {})
        headers["X-Correlation-ID"] = correlation_id

        logger.info(
            "API request",
            extra={
                "method": method,
                "endpoint": endpoint,
                "correlation_id": correlation_id,
            },
        )

        response = await self.client.request(method, endpoint, headers=headers, **kwargs)

        logger.info(
            "API response",
            extra={
                "method": method,
                "endpoint": endpoint,
                "status": response.status_code,
                "correlation_id": correlation_id,
            },
        )

        return response

    # Guild Management

    async def create_guild(
        self,
        guild_id: int,
        guild_name: str,
        prefix: str = "!",
        **kwargs: Any,
    ) -> GuildSchema:
        """Create a new guild.

        Args:
            guild_id: Discord guild ID
            guild_name: Discord guild name
            prefix: Command prefix
            **kwargs: Additional guild configuration

        Returns:
            Created guild schema

        Raises:
            APIError: If the API request fails
        """
        request = CreateGuildRequest(
            guild_id=guild_id,
            guild_name=guild_name,
            prefix=prefix,
            **kwargs,
        )

        try:
            response = await self._request(
                "POST",
                "/api/guilds",
                json=request.model_dump(),
            )
            response.raise_for_status()
            return GuildSchema.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            msg = f"Failed to create guild: {e.response.text}"
            logger.exception(msg, extra={"guild_id": guild_id, "status_code": e.response.status_code})
            raise APIError(msg, status_code=e.response.status_code) from e
        except httpx.RequestError as e:
            msg = f"Failed to connect to API service: {e!s}"
            logger.exception(msg, extra={"guild_id": guild_id})
            raise APIError(msg) from e

    async def get_guild(self, guild_id: int) -> GuildSchema | None:
        """Get guild by Discord ID.

        Args:
            guild_id: Discord guild ID

        Returns:
            Guild schema if found, None otherwise

        Raises:
            APIError: If the API request fails (excluding 404)
        """
        try:
            response = await self._request("GET", f"/api/guilds/{guild_id}")

            if response.status_code == HTTP_NOT_FOUND:
                return None

            response.raise_for_status()
            return GuildSchema.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            msg = f"Failed to get guild: {e.response.text}"
            logger.exception(msg, extra={"guild_id": guild_id, "status_code": e.response.status_code})
            raise APIError(msg, status_code=e.response.status_code) from e
        except httpx.RequestError as e:
            msg = f"Failed to connect to API service: {e!s}"
            logger.exception(msg, extra={"guild_id": guild_id})
            raise APIError(msg) from e

    async def update_guild(
        self,
        guild_id: UUID,
        **updates: Any,
    ) -> GuildSchema:
        """Update guild configuration.

        Args:
            guild_id: Guild UUID (not Discord ID)
            **updates: Fields to update

        Returns:
            Updated guild schema

        Raises:
            APIError: If the API request fails
        """
        request = UpdateGuildRequest(**updates)

        try:
            response = await self._request(
                "PATCH",
                f"/api/guilds/{guild_id}",
                json=request.model_dump(exclude_unset=True),
            )
            response.raise_for_status()
            return GuildSchema.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            msg = f"Failed to update guild: {e.response.text}"
            logger.exception(msg, extra={"guild_id": guild_id, "status_code": e.response.status_code})
            raise APIError(msg, status_code=e.response.status_code) from e
        except httpx.RequestError as e:
            msg = f"Failed to connect to API service: {e!s}"
            logger.exception(msg, extra={"guild_id": guild_id})
            raise APIError(msg) from e

    async def delete_guild(self, guild_id: UUID) -> None:
        """Delete a guild.

        Args:
            guild_id: Guild UUID (not Discord ID)

        Raises:
            APIError: If the API request fails
        """
        try:
            response = await self._request("DELETE", f"/api/guilds/{guild_id}")
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            msg = f"Failed to delete guild: {e.response.text}"
            logger.exception(msg, extra={"guild_id": guild_id, "status_code": e.response.status_code})
            raise APIError(msg, status_code=e.response.status_code) from e
        except httpx.RequestError as e:
            msg = f"Failed to connect to API service: {e!s}"
            logger.exception(msg, extra={"guild_id": guild_id})
            raise APIError(msg) from e

    async def get_or_create_guild(
        self,
        guild_id: int,
        guild_name: str,
        prefix: str = "!",
    ) -> GuildSchema:
        """Get guild or create if it doesn't exist.

        Args:
            guild_id: Discord guild ID
            guild_name: Discord guild name
            prefix: Command prefix

        Returns:
            Guild schema

        Raises:
            APIError: If the API request fails
        """
        # Try to get existing guild
        guild = await self.get_guild(guild_id)
        if guild is not None:
            return guild

        # Create new guild
        return await self.create_guild(
            guild_id=guild_id,
            guild_name=guild_name,
            prefix=prefix,
        )

    # Health Check

    async def health_check(self) -> dict[str, Any]:
        """Check API service health.

        Returns:
            Health check response

        Raises:
            APIError: If the API is unhealthy
        """
        try:
            response = await self._request("GET", "/health")
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            msg = f"API health check failed: {e!s}"
            logger.exception(msg)
            raise APIError(msg) from e
