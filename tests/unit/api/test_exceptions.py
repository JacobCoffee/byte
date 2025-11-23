"""Tests for exception types and handlers."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from byte_api.lib.exceptions import (
    ApplicationError,
    AuthorizationError,
    HealthCheckConfigurationError,
    MissingDependencyError,
    after_exception_hook_handler,
)

__all__ = [
    "TestExceptionHandlers",
    "TestExceptionTypes",
]


class TestExceptionTypes:
    """Tests for custom exception types."""

    def test_application_error_creation(self) -> None:
        """Test ApplicationError can be created."""
        error = ApplicationError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_authorization_error_creation(self) -> None:
        """Test AuthorizationError can be created."""
        error = AuthorizationError("Unauthorized access")
        assert str(error) == "Unauthorized access"
        assert isinstance(error, ApplicationError)

    def test_missing_dependency_error_default_config(self) -> None:
        """Test MissingDependencyError with default config."""
        error = MissingDependencyError("test-module")
        error_msg = str(error)

        assert "test-module" in error_msg
        assert "pip install byte-bot[test-module]" in error_msg
        assert isinstance(error, ApplicationError)
        assert isinstance(error, ValueError)

    def test_missing_dependency_error_custom_config(self) -> None:
        """Test MissingDependencyError with custom config name."""
        error = MissingDependencyError("test-module", config="custom-config")
        error_msg = str(error)

        assert "test-module" in error_msg
        assert "custom-config" in error_msg
        assert "pip install byte-bot[custom-config]" in error_msg

    def test_health_check_configuration_error(self) -> None:
        """Test HealthCheckConfigurationError can be created."""
        error = HealthCheckConfigurationError("Invalid health check config")
        assert str(error) == "Invalid health check config"
        assert isinstance(error, ApplicationError)


@pytest.mark.asyncio
class TestExceptionHandlers:
    """Tests for exception handler functions."""

    async def test_after_exception_hook_handler_ignores_application_error(self) -> None:
        """Test hook handler ignores ApplicationError (no logging)."""
        exc = ApplicationError("test")
        scope = Mock()

        # Should not raise, should not bind context vars
        await after_exception_hook_handler(exc, scope)
        # No assertion needed - just verify it doesn't crash

    async def test_after_exception_hook_handler_ignores_4xx_errors(self) -> None:
        """Test hook handler ignores client errors (4xx)."""
        from litestar.exceptions import HTTPException

        exc = HTTPException(detail="Not found", status_code=404)
        scope = Mock()

        # Should not bind context for client errors
        await after_exception_hook_handler(exc, scope)

    async def test_after_exception_hook_handler_handles_5xx_errors(self) -> None:
        """Test hook handler processes server errors (5xx)."""
        from litestar.exceptions import HTTPException

        exc = HTTPException(detail="Server error", status_code=500)
        scope = Mock()

        # Should bind context for server errors
        await after_exception_hook_handler(exc, scope)
