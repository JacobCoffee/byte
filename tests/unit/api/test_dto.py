"""Tests for DTO configuration helpers."""

from __future__ import annotations

from litestar.dto import DTOConfig

from byte_api.lib.dto import config

__all__ = [
    "TestDTOConfig",
]


class TestDTOConfig:
    """Tests for DTO config helper function."""

    def test_config_default_dataclass(self) -> None:
        """Test default DTO config creation."""
        dto_config = config()

        assert isinstance(dto_config, DTOConfig)
        # Default rename_strategy should be "camel"
        assert dto_config.rename_strategy == "camel"
        assert dto_config.max_nested_depth == 2

    def test_config_with_exclude(self) -> None:
        """Test DTO config with excluded fields."""
        dto_config = config(exclude={"password", "secret"})

        assert isinstance(dto_config, DTOConfig)
        assert "password" in dto_config.exclude
        assert "secret" in dto_config.exclude

    def test_config_with_rename_fields(self) -> None:
        """Test DTO config with field renaming."""
        dto_config = config(rename_fields={"id": "identifier", "name": "display_name"})

        assert isinstance(dto_config, DTOConfig)
        assert dto_config.rename_fields == {"id": "identifier", "name": "display_name"}

    def test_config_with_custom_rename_strategy(self) -> None:
        """Test DTO config with custom rename strategy."""
        dto_config = config(rename_strategy="pascal")

        assert isinstance(dto_config, DTOConfig)
        assert dto_config.rename_strategy == "pascal"

    def test_config_with_custom_max_nested_depth(self) -> None:
        """Test DTO config with custom max nested depth."""
        dto_config = config(max_nested_depth=5)

        assert isinstance(dto_config, DTOConfig)
        assert dto_config.max_nested_depth == 5

    def test_config_with_partial(self) -> None:
        """Test DTO config with partial flag."""
        dto_config = config(partial=True)

        assert isinstance(dto_config, DTOConfig)
        assert dto_config.partial is True

    def test_config_with_all_parameters(self) -> None:
        """Test DTO config with all parameters specified."""
        dto_config = config(
            backend="dataclass",
            exclude={"internal_field"},
            rename_fields={"old_name": "new_name"},
            rename_strategy="snake",
            max_nested_depth=3,
            partial=True,
        )

        assert isinstance(dto_config, DTOConfig)
        assert "internal_field" in dto_config.exclude
        assert dto_config.rename_fields == {"old_name": "new_name"}
        assert dto_config.rename_strategy == "snake"
        assert dto_config.max_nested_depth == 3
        assert dto_config.partial is True

    def test_config_dataclass_backend_explicit(self) -> None:
        """Test DTO config with explicit dataclass backend."""
        dto_config = config(backend="dataclass")

        assert isinstance(dto_config, DTOConfig)

    def test_config_none_values_ignored(self) -> None:
        """Test that None values don't override defaults."""
        dto_config = config(
            exclude=None,
            rename_fields=None,
            rename_strategy=None,
            max_nested_depth=None,
            partial=None,
        )

        assert isinstance(dto_config, DTOConfig)
        # Default values should be used
        assert dto_config.rename_strategy == "camel"
        assert dto_config.max_nested_depth == 2
