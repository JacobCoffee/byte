"""Tests for ORM utilities."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from byte_api.lib.db.orm import SlugKey, model_from_dict
from byte_common.models.guild import Guild

__all__ = [
    "TestModelFromDict",
    "TestSlugKeyMixin",
]


class TestModelFromDict:
    """Tests for model_from_dict utility function."""

    def test_model_from_dict_creates_instance(self) -> None:
        """Test model_from_dict creates model instance from dict."""
        result = model_from_dict(  # type: ignore[arg-type]
            Guild,
            guild_id=12345,
            guild_name="Test Guild",
            prefix="!",
        )

        assert isinstance(result, Guild)
        assert result.guild_id == 12345
        assert result.guild_name == "Test Guild"
        assert result.prefix == "!"

    def test_model_from_dict_ignores_unknown_fields(self) -> None:
        """Test model_from_dict ignores fields not in model."""
        result = model_from_dict(  # type: ignore[arg-type]
            Guild,
            guild_id=67890,
            guild_name="Another Guild",
            unknown_field="should be ignored",
            another_unknown="also ignored",
        )

        assert isinstance(result, Guild)
        assert result.guild_id == 67890
        assert result.guild_name == "Another Guild"
        # Unknown fields are ignored, no error raised

    def test_model_from_dict_with_none_values(self) -> None:
        """Test model_from_dict handles None values correctly."""
        result = model_from_dict(  # type: ignore[arg-type]
            Guild,
            guild_id=99999,
            guild_name="Guild with Nones",
            prefix=None,  # Optional field
        )

        assert isinstance(result, Guild)
        assert result.guild_id == 99999
        assert result.guild_name == "Guild with Nones"
        # None values are not set (skipped)

    def test_model_from_dict_partial_data(self) -> None:
        """Test model_from_dict with partial data (only required fields)."""
        result = model_from_dict(  # type: ignore[arg-type]
            Guild,
            guild_id=111111,
            guild_name="Minimal Guild",
        )

        assert isinstance(result, Guild)
        assert result.guild_id == 111111
        assert result.guild_name == "Minimal Guild"


class TestSlugKeyMixin:
    """Tests for SlugKey mixin."""

    def test_slug_key_mixin_has_slug_field(self) -> None:
        """Test that SlugKey mixin provides slug field."""
        # Create a test model using the mixin
        from byte_api.lib.db.orm import DatabaseModel

        class TestSlugModel(DatabaseModel, SlugKey):
            __tablename__ = "test_slug_model"
            name: Mapped[str] = mapped_column(String(100))

        # Verify slug field exists in model
        assert hasattr(TestSlugModel, "slug")

        # Create instance
        instance = TestSlugModel(slug="test-slug", name="Test")
        assert instance.slug == "test-slug"

    def test_slug_key_mixin_slug_is_unique(self) -> None:
        """Test that slug field is configured as unique."""
        from byte_api.lib.db.orm import DatabaseModel

        class TestSlugModel(DatabaseModel, SlugKey):
            __tablename__ = "test_slug_unique_model"
            name: Mapped[str] = mapped_column(String(100))

        # Check table column constraints
        slug_column = TestSlugModel.__table__.columns["slug"]
        assert slug_column.unique is True
        assert slug_column.nullable is False
        assert slug_column.index is True
