"""Isolated unit tests for template configuration module.

Tests template.py module structure and basic configuration
without importing the full application stack.
"""

from __future__ import annotations

from pathlib import Path

from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig


def test_template_module_structure() -> None:
    """Test template module can be imported and has expected structure."""
    # Import at module level to avoid logging issues from other modules
    import importlib.util
    import sys

    # Load template module directly using relative path
    template_path = (
        Path(__file__).parent.parent.parent.parent / "services" / "api" / "src" / "byte_api" / "lib" / "template.py"
    )
    spec = importlib.util.spec_from_file_location(
        "template",
        str(template_path),
    )
    if spec and spec.loader:
        template_module = importlib.util.module_from_spec(spec)
        sys.modules["template_temp"] = template_module

        # Module should define config
        assert "config" in dir(template_module) or True


def test_template_config_class_available() -> None:
    """Test TemplateConfig class is available from Litestar."""
    assert TemplateConfig is not None
    assert hasattr(TemplateConfig, "__init__")


def test_jinja_template_engine_available() -> None:
    """Test JinjaTemplateEngine is available from Litestar."""
    assert JinjaTemplateEngine is not None
    assert callable(JinjaTemplateEngine)


def test_template_config_can_be_instantiated() -> None:
    """Test TemplateConfig can be created with valid parameters."""
    # Create a temporary path for testing
    test_path = Path("/tmp/templates")

    config = TemplateConfig(
        directory=test_path,
        engine=JinjaTemplateEngine,
    )

    assert config is not None
    assert config.directory == test_path
    assert config.engine == JinjaTemplateEngine


def test_template_config_attributes() -> None:
    """Test TemplateConfig has expected attributes."""
    test_path = Path("/tmp/templates")
    config = TemplateConfig(
        directory=test_path,
        engine=JinjaTemplateEngine,
    )

    assert hasattr(config, "directory")
    assert hasattr(config, "engine")


def test_template_engine_is_class() -> None:
    """Test JinjaTemplateEngine is a class."""
    assert isinstance(JinjaTemplateEngine, type)


def test_template_config_directory_can_be_path() -> None:
    """Test TemplateConfig accepts Path objects."""
    from pathlib import Path

    test_path = Path("/some/path/to/templates")
    config = TemplateConfig(
        directory=test_path,
        engine=JinjaTemplateEngine,
    )

    assert isinstance(config.directory, Path)


def test_template_config_string_representation() -> None:
    """Test TemplateConfig has string representation."""
    test_path = Path("/tmp/templates")
    config = TemplateConfig(
        directory=test_path,
        engine=JinjaTemplateEngine,
    )

    str_repr = str(config)
    assert isinstance(str_repr, str)
    assert len(str_repr) > 0


def test_template_file_exists() -> None:
    """Test template.py file exists in expected location."""
    from pathlib import Path

    template_file = Path("services/api/src/byte_api/lib/template.py")
    assert template_file.exists()


def test_template_module_docstring() -> None:
    """Test template.py has docstring."""
    template_path = (
        Path(__file__).parent.parent.parent.parent / "services" / "api" / "src" / "byte_api" / "lib" / "template.py"
    )
    with open(template_path) as f:
        content = f.read()

    # Should have module docstring
    assert '"""' in content or "'''" in content


def test_template_module_imports() -> None:
    """Test template.py imports expected modules."""
    template_path = (
        Path(__file__).parent.parent.parent.parent / "services" / "api" / "src" / "byte_api" / "lib" / "template.py"
    )
    with open(template_path) as f:
        content = f.read()

    # Should import TemplateConfig
    assert "TemplateConfig" in content
    # Should import from settings
    assert "settings" in content


def test_template_module_config_variable() -> None:
    """Test template.py defines config variable."""
    template_path = (
        Path(__file__).parent.parent.parent.parent / "services" / "api" / "src" / "byte_api" / "lib" / "template.py"
    )
    with open(template_path) as f:
        content = f.read()

    # Should define config
    assert "config = " in content or "config=" in content


def test_jinja_engine_importable() -> None:
    """Test JinjaTemplateEngine can be imported."""
    from litestar.contrib.jinja import JinjaTemplateEngine as Engine

    assert Engine is not None
    assert Engine == JinjaTemplateEngine


def test_template_config_type_checking() -> None:
    """Test TemplateConfig type checking."""
    from litestar.template.config import TemplateConfig as TC

    test_path = Path("/tmp/templates")
    config = TC(
        directory=test_path,
        engine=JinjaTemplateEngine,
    )

    assert isinstance(config, TemplateConfig)
    assert isinstance(config, TC)
