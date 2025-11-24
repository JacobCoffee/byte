"""HTTP client for communicating with the Byte API service."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Self, TypedDict

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from byte_common.schemas.guild import CreateGuildRequest, GuildSchema, UpdateGuildRequest

if TYPE_CHECKING:
    from uuid import UUID

__all__ = ("APIError", "ByteAPIClient", "RetryStats")


class RetryStats(TypedDict):
    """Statistics tracking for retry attempts."""

    total_retries: int
    failed_requests: int
    retried_methods: dict[str, int]


logger = logging.getLogger(__name__)

# HTTP status codes
HTTP_NOT_FOUND = 404
HTTP_CLIENT_ERROR_MIN = 400
HTTP_CLIENT_ERROR_MAX = 499
HTTP_SERVER_ERROR_MIN = 500


def _should_retry(exception: BaseException) -> bool:
    """Determine if an exception should trigger a retry.

    Retries on:
    - HTTP 5xx errors (server errors)
    - Connection errors (ConnectError, ConnectTimeout, ReadTimeout)

    Does NOT retry on:
    - HTTP 4xx errors (client errors - bad request, auth, etc.)

    Args:
        exception: The exception to evaluate

    Returns:
        True if the request should be retried, False otherwise
    """
    # Retry on connection errors
    if isinstance(exception, (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout)):
        return True

    # Retry on HTTP 5xx errors (server errors)
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code >= HTTP_SERVER_ERROR_MIN

    # Don't retry on other errors (including 4xx)
    return False


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
    replacing direct database access. Includes automatic retry logic with exponential
    backoff for transient failures.

    Retry Configuration:
        - Max retries: 3 attempts
        - Backoff: Exponential (1s, 2s, 4s, max 10s)
        - Retryable errors: HTTP 5xx, connection errors
        - Non-retryable: HTTP 4xx (client errors)
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
        self.retry_stats: RetryStats = {
            "total_retries": 0,
            "failed_requests": 0,
            "retried_methods": {},
        }

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        await self.close()

    def _track_retry(self, method_name: str) -> None:
        """Track a retry attempt for statistics.

        Args:
            method_name: Name of the method being retried
        """
        self.retry_stats["total_retries"] += 1
        if method_name not in self.retry_stats["retried_methods"]:
            self.retry_stats["retried_methods"][method_name] = 0
        self.retry_stats["retried_methods"][method_name] += 1

    def _track_failure(self) -> None:
        """Track a failed request for statistics."""
        self.retry_stats["failed_requests"] += 1

    # Guild Management

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(_should_retry),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
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
            response = await self.client.post(
                "/api/guilds",
                json=request.model_dump(),
            )
            response.raise_for_status()
            return GuildSchema.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            # Track retry if applicable
            if _should_retry(e):
                self._track_retry("create_guild")
            else:
                self._track_failure()

            msg = f"Failed to create guild: {e.response.text}"
            logger.exception(msg, extra={"guild_id": guild_id, "status_code": e.response.status_code})
            raise APIError(msg, status_code=e.response.status_code) from e
        except httpx.RequestError as e:
            self._track_retry("create_guild")
            msg = f"Failed to connect to API service: {e!s}"
            logger.exception(msg, extra={"guild_id": guild_id})
            raise APIError(msg) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(_should_retry),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
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
            response = await self.client.get(f"/api/guilds/{guild_id}")

            if response.status_code == HTTP_NOT_FOUND:
                return None

            response.raise_for_status()
            return GuildSchema.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            # Track retry if applicable
            if _should_retry(e):
                self._track_retry("get_guild")
            else:
                self._track_failure()

            msg = f"Failed to get guild: {e.response.text}"
            logger.exception(msg, extra={"guild_id": guild_id, "status_code": e.response.status_code})
            raise APIError(msg, status_code=e.response.status_code) from e
        except httpx.RequestError as e:
            self._track_retry("get_guild")
            msg = f"Failed to connect to API service: {e!s}"
            logger.exception(msg, extra={"guild_id": guild_id})
            raise APIError(msg) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(_should_retry),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
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
            response = await self.client.patch(
                f"/api/guilds/{guild_id}",
                json=request.model_dump(exclude_unset=True),
            )
            response.raise_for_status()
            return GuildSchema.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            # Track retry if applicable
            if _should_retry(e):
                self._track_retry("update_guild")
            else:
                self._track_failure()

            msg = f"Failed to update guild: {e.response.text}"
            logger.exception(msg, extra={"guild_id": guild_id, "status_code": e.response.status_code})
            raise APIError(msg, status_code=e.response.status_code) from e
        except httpx.RequestError as e:
            self._track_retry("update_guild")
            msg = f"Failed to connect to API service: {e!s}"
            logger.exception(msg, extra={"guild_id": guild_id})
            raise APIError(msg) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(_should_retry),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def delete_guild(self, guild_id: UUID) -> None:
        """Delete a guild.

        Args:
            guild_id: Guild UUID (not Discord ID)

        Raises:
            APIError: If the API request fails
        """
        try:
            response = await self.client.delete(f"/api/guilds/{guild_id}")
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            # Track retry if applicable
            if _should_retry(e):
                self._track_retry("delete_guild")
            else:
                self._track_failure()

            msg = f"Failed to delete guild: {e.response.text}"
            logger.exception(msg, extra={"guild_id": guild_id, "status_code": e.response.status_code})
            raise APIError(msg, status_code=e.response.status_code) from e
        except httpx.RequestError as e:
            self._track_retry("delete_guild")
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception(_should_retry),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def health_check(self) -> dict[str, Any]:
        """Check API service health.

        Returns:
            Health check response

        Raises:
            APIError: If the API is unhealthy
        """
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Track retry if applicable
            if _should_retry(e):
                self._track_retry("health_check")
            else:
                self._track_failure()

            msg = f"API health check failed: {e!s}"
            logger.exception(msg)
            raise APIError(msg) from e
        except httpx.RequestError as e:
            self._track_retry("health_check")
            msg = f"API health check failed: {e!s}"
            logger.exception(msg)
            raise APIError(msg) from e
