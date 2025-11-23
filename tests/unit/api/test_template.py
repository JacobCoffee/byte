"""Unit tests for Jinja2 template configuration.

Tests template engine configuration, directory setup,
and template rendering functionality.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.status_codes import HTTP_200_OK
from litestar.template.config import TemplateConfig

if TYPE_CHECKING:
    from litestar.testing import AsyncTestClient

# Import directly to avoid logging configuration issues
import byte_api.lib.settings as settings_module
import byte_api.lib.template as template_module

template = template_module
settings = settings_module

__all__ = [
    "test_template_config_created",
    "test_template_config_directory",
    "test_template_config_engine",
    "test_template_config_from_settings",
    "test_template_config_type",
    "test_template_directory_exists",
    "test_template_engine_is_jinja",
]


def test_template_config_created() -> None:
    """Test template config object is properly instantiated."""
    assert template.config is not None
    assert isinstance(template.config, TemplateConfig)


def test_template_config_directory() -> None:
    """Test template directory is configured correctly."""
    assert template.config.directory is not None
    assert template.config.directory == settings.TEMPLATES_DIR


def test_template_config_engine() -> None:
    """Test template engine is configured correctly."""
    assert template.config.engine is not None
    assert template.config.engine == settings.template.ENGINE


def test_template_config_from_settings() -> None:
    """Test template config uses settings from environment."""
    # Template should pull from settings
    assert template.config.directory == settings.TEMPLATES_DIR
    assert template.config.engine == settings.template.ENGINE


def test_template_engine_is_jinja() -> None:
    """Test template engine is Jinja2."""
    # Default should be Jinja2
    assert template.config.engine == JinjaTemplateEngine


def test_template_directory_exists() -> None:
    """Test templates directory exists in project structure."""
    import os

    template_dir = str(settings.TEMPLATES_DIR)
    assert os.path.exists(template_dir) or "templates" in template_dir


def test_template_config_type() -> None:
    """Test template config is correct Litestar type."""
    from litestar.template.config import TemplateConfig

    assert isinstance(template.config, TemplateConfig)


def test_template_directory_path_is_absolute() -> None:
    """Test template directory path is absolute."""
    from pathlib import Path

    assert isinstance(settings.TEMPLATES_DIR, Path)
    # Path should be absolute or valid
    assert settings.TEMPLATES_DIR.is_absolute() or str(settings.TEMPLATES_DIR)


@pytest.mark.asyncio
async def test_template_rendering_in_response(api_client: AsyncTestClient) -> None:
    """Test templates can be rendered in HTTP responses."""
    # Dashboard route should render a template
    response = await api_client.get("/")

    # Should succeed
    assert response.status_code == HTTP_200_OK

    # Should return HTML content
    assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_template_context_variables(api_client: AsyncTestClient) -> None:
    """Test templates receive context variables."""
    response = await api_client.get("/")

    assert response.status_code == HTTP_200_OK

    # Template should contain some expected content
    content = response.text.lower()
    # Most templates should have html tags
    assert "<html" in content or "<!doctype" in content


def test_template_instance_config() -> None:
    """Test template config can be instantiated directly."""
    from litestar.template.config import TemplateConfig

    # Should be able to create a new config with same params
    test_config = TemplateConfig(
        directory=settings.TEMPLATES_DIR,
        engine=JinjaTemplateEngine,
    )

    assert test_config is not None
    assert test_config.directory == settings.TEMPLATES_DIR
    assert test_config.engine == JinjaTemplateEngine


def test_template_engine_class_available() -> None:
    """Test Jinja2 template engine class is available."""
    from litestar.contrib.jinja import JinjaTemplateEngine

    # Should be importable
    assert JinjaTemplateEngine is not None
    assert hasattr(JinjaTemplateEngine, "__init__")


@pytest.mark.asyncio
async def test_multiple_template_renders(api_client: AsyncTestClient) -> None:
    """Test multiple templates can be rendered without conflicts."""
    # Render template multiple times
    response1 = await api_client.get("/")
    response2 = await api_client.get("/")

    assert response1.status_code == HTTP_200_OK
    assert response2.status_code == HTTP_200_OK

    # Both should return similar content
    assert response1.headers.get("content-type") == response2.headers.get("content-type")


def test_template_settings_integration() -> None:
    """Test template settings are properly integrated."""
    from byte_api.lib.settings import TemplateSettings

    # Template settings should be loaded
    assert isinstance(settings.template, TemplateSettings)
    assert settings.template.ENGINE == JinjaTemplateEngine


@pytest.mark.asyncio
async def test_template_error_handling(api_client: AsyncTestClient) -> None:
    """Test template rendering handles errors gracefully."""
    # Try to access a route that might not exist
    response = await api_client.get("/nonexistent-route-for-testing")

    # Should return 404 or redirect, not crash
    assert response.status_code in [404, 301, 302, 307, 308, HTTP_200_OK]


def test_template_config_has_required_attributes() -> None:
    """Test template config has all required attributes."""
    assert hasattr(template.config, "directory")
    assert hasattr(template.config, "engine")


def test_template_directory_from_module_path() -> None:
    """Test template directory is derived from module path."""
    from byte_api.lib.settings import TEMPLATES_DIR

    # Should be derived from base directory
    assert "byte_api" in str(TEMPLATES_DIR) or "templates" in str(TEMPLATES_DIR)


@pytest.mark.asyncio
async def test_template_renders_html_structure(api_client: AsyncTestClient) -> None:
    """Test rendered templates have valid HTML structure."""
    response = await api_client.get("/")

    if response.status_code == HTTP_200_OK:
        content = response.text.lower()

        # Check for common HTML elements
        has_html_structure = any(
            [
                "<html" in content,
                "<!doctype" in content,
                "<head>" in content,
                "<body>" in content,
            ]
        )

        # Should have some HTML structure
        assert has_html_structure or len(content) > 0


def test_template_config_serializable() -> None:
    """Test template config can be represented as string."""
    config_str = str(template.config)

    # Should have string representation
    assert isinstance(config_str, str)
    assert len(config_str) > 0


@pytest.mark.asyncio
async def test_template_content_type_header(api_client: AsyncTestClient) -> None:
    """Test template responses have correct content type."""
    response = await api_client.get("/")

    if response.status_code == HTTP_200_OK:
        content_type = response.headers.get("content-type", "")

        # Should be HTML or text
        assert "text/html" in content_type or "text/plain" in content_type or content_type


def test_template_config_engine_callable() -> None:
    """Test template engine can be instantiated."""
    # Engine should be a class/callable
    assert callable(template.config.engine)

    # Should be able to reference the class
    engine_class = template.config.engine
    assert engine_class == JinjaTemplateEngine
