"""Basic sanity tests for the test suite."""

import pytest


def test_pass():
    """Basic passing test to verify test infrastructure."""
    assert True


def test_imports():
    """Test that core modules can be imported."""
    # Test server imports
    from byte_bot.server.domain.db import models

    assert models is not None

    # Test bot imports
    from byte_bot.byte import bot

    assert bot is not None


@pytest.mark.asyncio
async def test_async_support():
    """Test that async test support is working."""

    # Simple async test to verify pytest-asyncio is configured
    async def async_function():
        return True

    result = await async_function()
    assert result is True
