"""Test that all byte-common imports work correctly."""

from __future__ import annotations


class TestImports:
    """Test package imports."""

    def test_import_models(self) -> None:
        """Test importing models."""
        from byte_common.models import Guild, User
        from byte_common.models.forum_config import ForumConfig
        from byte_common.models.github_config import GitHubConfig

        assert Guild is not None
        assert User is not None
        assert GitHubConfig is not None
        assert ForumConfig is not None

    def test_import_schemas(self) -> None:
        """Test importing schemas."""
        from byte_common.schemas.guild import CreateGuildRequest, GuildSchema, UpdateGuildRequest

        assert GuildSchema is not None
        assert CreateGuildRequest is not None
        assert UpdateGuildRequest is not None

    def test_import_utils(self) -> None:
        """Test importing utility functions."""
        from byte_common.utils.encoding import encode_to_base64
        from byte_common.utils.strings import camel_case, case_insensitive_string_compare, slugify

        assert slugify is not None
        assert camel_case is not None
        assert case_insensitive_string_compare is not None
        assert encode_to_base64 is not None

    def test_import_settings(self) -> None:
        """Test importing settings."""
        from byte_common.settings.base import BaseSettings
        from byte_common.settings.database import DatabaseSettings

        assert BaseSettings is not None
        assert DatabaseSettings is not None

    def test_import_constants(self) -> None:
        """Test importing constants."""
        from byte_common import constants

        assert constants is not None

    def test_top_level_imports(self) -> None:
        """Test top-level package imports."""
        import byte_common

        assert byte_common.__version__ is not None
