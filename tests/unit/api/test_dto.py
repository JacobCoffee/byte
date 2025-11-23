"""Tests for DTO configuration helpers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from litestar.dto import DTOConfig

# Import the dto module directly without triggering __init__.py
dto_path = Path(__file__).parent.parent.parent.parent / "services" / "api" / "src" / "byte_api" / "lib" / "dto.py"
spec = importlib.util.spec_from_file_location("dto", dto_path)
dto = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules["dto"] = dto
spec.loader.exec_module(dto)  # type: ignore[union-attr]

config = dto.config

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

    def test_config_with_empty_exclude(self) -> None:
        """Test DTO config with empty exclude set."""
        dto_config = config(exclude=set())

        assert isinstance(dto_config, DTOConfig)
        # Empty set is falsy, so exclude should not be in config
        assert not hasattr(dto_config, "exclude") or dto_config.exclude == set()

    def test_config_with_empty_rename_fields(self) -> None:
        """Test DTO config with empty rename_fields dict."""
        dto_config = config(rename_fields={})

        assert isinstance(dto_config, DTOConfig)
        # Empty dict is falsy, so rename_fields should not be set

    def test_config_multiple_exclude_fields(self) -> None:
        """Test DTO config with multiple excluded fields."""
        dto_config = config(exclude={"field1", "field2", "field3", "field4"})

        assert isinstance(dto_config, DTOConfig)
        assert "field1" in dto_config.exclude
        assert "field2" in dto_config.exclude
        assert "field3" in dto_config.exclude
        assert "field4" in dto_config.exclude

    def test_config_multiple_rename_fields(self) -> None:
        """Test DTO config with multiple field renamings."""
        dto_config = config(
            rename_fields={
                "id": "identifier",
                "name": "display_name",
                "created_at": "createdAt",
                "updated_at": "updatedAt",
            }
        )

        assert isinstance(dto_config, DTOConfig)
        assert len(dto_config.rename_fields) == 4
        assert dto_config.rename_fields["id"] == "identifier"
        assert dto_config.rename_fields["created_at"] == "createdAt"

    def test_config_with_zero_max_nested_depth(self) -> None:
        """Test DTO config with zero max_nested_depth."""
        # Zero is falsy, should use default
        dto_config = config(max_nested_depth=0)

        assert isinstance(dto_config, DTOConfig)
        # 0 is falsy in the config function, so default should be used
        assert dto_config.max_nested_depth == 2

    def test_config_with_large_max_nested_depth(self) -> None:
        """Test DTO config with large max_nested_depth."""
        dto_config = config(max_nested_depth=100)

        assert isinstance(dto_config, DTOConfig)
        assert dto_config.max_nested_depth == 100

    def test_config_partial_false(self) -> None:
        """Test DTO config with partial=False."""
        # False is falsy, should not be set
        dto_config = config(partial=False)

        assert isinstance(dto_config, DTOConfig)
        # False is falsy in the config function

    def test_config_all_rename_strategies(self) -> None:
        """Test DTO config with various rename strategies."""
        for strategy in ["camel", "pascal", "snake"]:
            dto_config = config(rename_strategy=strategy)
            assert dto_config.rename_strategy == strategy

    def test_config_combined_exclude_and_rename(self) -> None:
        """Test DTO config with both exclude and rename_fields."""
        dto_config = config(exclude={"password", "secret"}, rename_fields={"id": "identifier"})

        assert isinstance(dto_config, DTOConfig)
        assert "password" in dto_config.exclude
        assert "secret" in dto_config.exclude
        assert dto_config.rename_fields["id"] == "identifier"

    def test_config_combined_all_truthy_parameters(self) -> None:
        """Test DTO config with all truthy parameters set."""
        dto_config = config(
            backend="dataclass",
            exclude={"field1"},
            rename_fields={"old": "new"},
            rename_strategy="pascal",
            max_nested_depth=10,
            partial=True,
        )

        assert isinstance(dto_config, DTOConfig)
        assert "field1" in dto_config.exclude
        assert dto_config.rename_fields["old"] == "new"
        assert dto_config.rename_strategy == "pascal"
        assert dto_config.max_nested_depth == 10
        assert dto_config.partial is True

    def test_config_override_default_rename_strategy(self) -> None:
        """Test that custom rename_strategy overrides default."""
        # Default is "camel"
        default_config = config()
        assert default_config.rename_strategy == "camel"

        # Override with "snake"
        custom_config = config(rename_strategy="snake")
        assert custom_config.rename_strategy == "snake"

    def test_config_override_default_max_nested_depth(self) -> None:
        """Test that custom max_nested_depth overrides default."""
        # Default is 2
        default_config = config()
        assert default_config.max_nested_depth == 2

        # Override with 5
        custom_config = config(max_nested_depth=5)
        assert custom_config.max_nested_depth == 5
