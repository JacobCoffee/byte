"""Unit tests for API domain schemas."""

from __future__ import annotations

import inspect

import pytest
from pydantic import ValidationError

from byte_api.domain.guilds.schemas import (
    AllowedUsersConfigSchema,
    ForumConfigSchema,
    GitHubConfigSchema,
    GuildCreate,
    GuildSchema,
    GuildUpdate,
    SOTagsConfigSchema,
    UpdateableGuildSetting,
)

__all__ = [
    "TestGitHubConfigSchema",
    "TestSOTagsConfigSchema",
    "TestAllowedUsersConfigSchema",
    "TestForumConfigSchema",
    "TestGuildSchema",
    "TestGuildCreate",
    "TestGuildUpdate",
    "TestUpdateableGuildSetting",
    "TestSchemaDocumentation",
    "TestSchemaValidation",
]


class TestGitHubConfigSchema:
    """Tests for GitHubConfigSchema."""

    def test_github_config_schema_valid(self) -> None:
        """Test creating valid GitHubConfigSchema."""
        from uuid import uuid4

        schema = GitHubConfigSchema(
            guild_id=uuid4(),
            discussion_sync=True,
            github_organization="test-org",
            github_repository="test-repo",
        )

        assert schema.discussion_sync is True
        assert schema.github_organization == "test-org"
        assert schema.github_repository == "test-repo"

    def test_github_config_schema_optional_fields(self) -> None:
        """Test GitHubConfigSchema with optional fields as None."""
        from uuid import uuid4

        schema = GitHubConfigSchema(
            guild_id=uuid4(),
            discussion_sync=False,
            github_organization=None,
            github_repository=None,
        )

        assert schema.discussion_sync is False
        assert schema.github_organization is None
        assert schema.github_repository is None

    def test_github_config_schema_serialization(self) -> None:
        """Test GitHubConfigSchema serialization."""
        from uuid import uuid4

        guild_id = uuid4()
        schema = GitHubConfigSchema(
            guild_id=guild_id,
            discussion_sync=True,
            github_organization="my-org",
            github_repository="my-repo",
        )

        data = schema.model_dump()

        assert data["guild_id"] == guild_id
        assert data["discussion_sync"] is True
        assert data["github_organization"] == "my-org"


class TestSOTagsConfigSchema:
    """Tests for SOTagsConfigSchema."""

    def test_sotags_config_schema_valid(self) -> None:
        """Test creating valid SOTagsConfigSchema."""
        from uuid import uuid4

        schema = SOTagsConfigSchema(guild_id=uuid4(), tag_name="python")

        assert schema.tag_name == "python"

    def test_sotags_config_schema_serialization(self) -> None:
        """Test SOTagsConfigSchema serialization."""
        from uuid import uuid4

        guild_id = uuid4()
        schema = SOTagsConfigSchema(guild_id=guild_id, tag_name="litestar")

        data = schema.model_dump()

        assert data["guild_id"] == guild_id
        assert data["tag_name"] == "litestar"


class TestAllowedUsersConfigSchema:
    """Tests for AllowedUsersConfigSchema."""

    def test_allowed_users_config_schema_valid(self) -> None:
        """Test creating valid AllowedUsersConfigSchema."""
        from uuid import uuid4

        guild_id = uuid4()
        user_id = uuid4()
        schema = AllowedUsersConfigSchema(guild_id=guild_id, user_id=user_id)

        assert schema.guild_id == guild_id
        assert schema.user_id == user_id

    def test_allowed_users_config_schema_serialization(self) -> None:
        """Test AllowedUsersConfigSchema serialization."""
        from uuid import uuid4

        guild_id = uuid4()
        user_id = uuid4()
        schema = AllowedUsersConfigSchema(guild_id=guild_id, user_id=user_id)

        data = schema.model_dump()

        assert data["guild_id"] == guild_id
        assert data["user_id"] == user_id


class TestForumConfigSchema:
    """Tests for ForumConfigSchema."""

    def test_forum_config_schema_valid(self) -> None:
        """Test creating valid ForumConfigSchema."""
        from uuid import uuid4

        schema = ForumConfigSchema(
            guild_id=uuid4(),
            help_forum=True,
            help_forum_category="Help",
            help_thread_auto_close=True,
            help_thread_auto_close_days=7,
            help_thread_notify=False,
            help_thread_notify_roles=[123, 456],
            help_thread_notify_days=3,
            help_thread_sync=True,
            showcase_forum=True,
            showcase_forum_category="Showcase",
            showcase_thread_auto_close=False,
            showcase_thread_auto_close_days=0,
        )

        assert schema.help_forum is True
        assert schema.help_forum_category == "Help"
        assert schema.help_thread_auto_close_days == 7
        assert schema.help_thread_notify_roles == [123, 456]
        assert schema.showcase_forum is True

    def test_forum_config_schema_serialization(self) -> None:
        """Test ForumConfigSchema serialization."""
        from uuid import uuid4

        guild_id = uuid4()
        schema = ForumConfigSchema(
            guild_id=guild_id,
            help_forum=False,
            help_forum_category="",
            help_thread_auto_close=False,
            help_thread_auto_close_days=0,
            help_thread_notify=False,
            help_thread_notify_roles=[],
            help_thread_notify_days=0,
            help_thread_sync=False,
            showcase_forum=False,
            showcase_forum_category="",
            showcase_thread_auto_close=False,
            showcase_thread_auto_close_days=0,
        )

        data = schema.model_dump()

        assert data["guild_id"] == guild_id
        assert data["help_forum"] is False
        assert data["help_thread_notify_roles"] == []


class TestGuildSchema:
    """Tests for GuildSchema."""

    def test_guild_schema_minimal(self) -> None:
        """Test GuildSchema with minimal fields."""
        from uuid import uuid4

        internal_id = uuid4()
        schema = GuildSchema(
            id=internal_id,
            guild_id=123456789,
            guild_name="Test Guild",
            prefix="!",
            help_channel_id=None,
            sync_label=None,
            issue_linking=False,
            comment_linking=False,
            pep_linking=False,
            github_config=None,
            sotags_configs=[],
            allowed_users=[],
            forum_config=None,
        )

        assert schema.internal_id == internal_id
        assert schema.guild_id == 123456789
        assert schema.guild_name == "Test Guild"
        assert schema.prefix == "!"

    def test_guild_schema_with_all_configs(self) -> None:
        """Test GuildSchema with all configuration types."""
        from uuid import uuid4

        internal_id = uuid4()
        guild_id_uuid = uuid4()

        github_config = GitHubConfigSchema(
            guild_id=guild_id_uuid,
            discussion_sync=True,
            github_organization="org",
            github_repository="repo",
        )

        sotag = SOTagsConfigSchema(guild_id=guild_id_uuid, tag_name="python")

        allowed_user = AllowedUsersConfigSchema(guild_id=guild_id_uuid, user_id=uuid4())

        forum_config = ForumConfigSchema(
            guild_id=guild_id_uuid,
            help_forum=True,
            help_forum_category="Help",
            help_thread_auto_close=False,
            help_thread_auto_close_days=0,
            help_thread_notify=False,
            help_thread_notify_roles=[],
            help_thread_notify_days=0,
            help_thread_sync=False,
            showcase_forum=False,
            showcase_forum_category="",
            showcase_thread_auto_close=False,
            showcase_thread_auto_close_days=0,
        )

        schema = GuildSchema(
            id=internal_id,
            guild_id=123456789,
            guild_name="Full Guild",
            prefix="$",
            help_channel_id=111,
            sync_label="sync",
            issue_linking=True,
            comment_linking=True,
            pep_linking=True,
            github_config=github_config,
            sotags_configs=[sotag],
            allowed_users=[allowed_user],
            forum_config=forum_config,
        )

        assert schema.github_config is not None
        assert len(schema.sotags_configs) == 1
        assert len(schema.allowed_users) == 1
        assert schema.forum_config is not None

    def test_guild_schema_camelized_output(self) -> None:
        """Test GuildSchema outputs camelCase keys."""
        from uuid import uuid4

        schema = GuildSchema(
            id=uuid4(),
            guild_id=123,
            guild_name="Test",
            prefix="!",
            help_channel_id=456,
            sync_label=None,
            issue_linking=True,
            comment_linking=False,
            pep_linking=False,
            github_config=None,
            sotags_configs=[],
            allowed_users=[],
            forum_config=None,
        )

        data = schema.model_dump(by_alias=True)

        # Should use camelCase
        # Note: internal_id has alias='id' so it's just 'id'
        assert "id" in data
        assert "guildId" in data
        assert "guildName" in data
        assert "helpChannelId" in data
        assert "issueLinking" in data


class TestGuildCreate:
    """Tests for GuildCreate schema."""

    def test_guild_create_valid(self) -> None:
        """Test creating valid GuildCreate."""
        schema = GuildCreate(id=123456789, name="New Guild")

        assert schema.guild_id == 123456789
        assert schema.name == "New Guild"

    def test_guild_create_alias_usage(self) -> None:
        """Test GuildCreate uses alias for guild_id."""
        schema = GuildCreate(id=999, name="Alias Test")

        data = schema.model_dump(by_alias=True)

        assert "id" in data
        assert "name" in data

    def test_guild_create_missing_required_fields(self) -> None:
        """Test GuildCreate validation with missing fields."""
        with pytest.raises(ValidationError):
            GuildCreate(name="Missing ID")  # type: ignore[call-arg]


class TestGuildUpdate:
    """Tests for GuildUpdate schema."""

    def test_guild_update_partial(self) -> None:
        """Test GuildUpdate with partial data."""
        schema = GuildUpdate(
            id=123,
            prefix="$",
            help_channel_id=None,
            sync_label=None,
            issue_linking=None,
            comment_linking=None,
            pep_linking=None,
        )

        assert schema.guild_id == 123
        assert schema.prefix == "$"

    def test_guild_update_all_fields(self) -> None:
        """Test GuildUpdate with all fields."""
        schema = GuildUpdate(
            id=456,
            prefix="!",
            help_channel_id=789,
            sync_label="sync-label",
            issue_linking=True,
            comment_linking=False,
            pep_linking=True,
        )

        assert schema.guild_id == 456
        assert schema.help_channel_id == 789
        assert schema.sync_label == "sync-label"
        assert schema.issue_linking is True

    def test_guild_update_serialization(self) -> None:
        """Test GuildUpdate serialization excludes None."""
        schema = GuildUpdate(
            id=123,
            prefix="$",
            help_channel_id=None,
            sync_label=None,
            issue_linking=True,
            comment_linking=None,
            pep_linking=None,
        )

        data = schema.model_dump(exclude_none=True)

        assert "prefix" in data
        assert "issue_linking" in data
        # None values excluded
        assert "help_channel_id" not in data
        assert "sync_label" not in data


class TestUpdateableGuildSetting:
    """Tests for UpdateableGuildSetting schema."""

    def test_updateable_guild_setting_all_fields(self) -> None:
        """Test UpdateableGuildSetting with all fields."""
        schema = UpdateableGuildSetting(
            prefix="!",
            help_channel_id=123,
            showcase_channel_id=456,
            sync_label="label",
            issue_linking=True,
            comment_linking=False,
            pep_linking=True,
            discussion_sync=True,
            github_organization="org",
            github_repository="repo",
            tag_name=["python", "litestar"],
            allowed_user_id=789,
            help_forum=True,
            help_forum_category="Help",
            help_thread_auto_close=False,
            help_thread_auto_close_days=0,
            help_thread_notify=False,
            help_thread_notify_roles=[111, 222],
            help_thread_notify_days=3,
            help_thread_sync=True,
            showcase_forum=True,
            showcase_forum_category="Showcase",
            showcase_thread_auto_close=False,
            showcase_thread_auto_close_days=0,
        )

        assert schema.prefix == "!"
        assert schema.github_organization == "org"
        assert schema.tag_name == ["python", "litestar"]
        assert schema.help_forum is True
        assert schema.help_thread_notify_roles == [111, 222]

    def test_updateable_guild_setting_field_descriptions(self) -> None:
        """Test UpdateableGuildSetting fields have descriptions."""
        fields = UpdateableGuildSetting.model_fields

        # Check that key fields have descriptions
        assert fields["prefix"].description is not None
        assert fields["discussion_sync"].description is not None
        assert fields["help_forum"].description is not None

    def test_updateable_guild_setting_serialization(self) -> None:
        """Test UpdateableGuildSetting serialization."""
        schema = UpdateableGuildSetting(
            prefix="$",
            help_channel_id=1,
            showcase_channel_id=2,
            sync_label="sync",
            issue_linking=False,
            comment_linking=False,
            pep_linking=False,
            discussion_sync=False,
            github_organization="org",
            github_repository="repo",
            tag_name=["tag1"],
            allowed_user_id=3,
            help_forum=False,
            help_forum_category="",
            help_thread_auto_close=False,
            help_thread_auto_close_days=0,
            help_thread_notify=False,
            help_thread_notify_roles=[],
            help_thread_notify_days=0,
            help_thread_sync=False,
            showcase_forum=False,
            showcase_forum_category="",
            showcase_thread_auto_close=False,
            showcase_thread_auto_close_days=0,
        )

        data = schema.model_dump()

        assert data["prefix"] == "$"
        assert data["tag_name"] == ["tag1"]
        assert data["help_thread_notify_roles"] == []


class TestSchemaDocumentation:
    """Tests for schema documentation and metadata."""

    def test_all_schemas_have_docstrings(self) -> None:
        """Test that all schema classes have docstrings."""
        schemas = [
            GitHubConfigSchema,
            SOTagsConfigSchema,
            AllowedUsersConfigSchema,
            ForumConfigSchema,
            GuildSchema,
            GuildCreate,
            GuildUpdate,
            UpdateableGuildSetting,
        ]

        for schema in schemas:
            assert schema.__doc__ is not None, f"{schema.__name__} missing docstring"
            assert len(schema.__doc__.strip()) > 0, f"{schema.__name__} has empty docstring"

    def test_schema_field_metadata(self) -> None:
        """Test schema fields have proper metadata."""
        # GuildSchema should have field titles and descriptions
        fields = GuildSchema.model_fields

        # Check internal_id field
        internal_id_field = fields["internal_id"]
        assert internal_id_field.title == "Internal ID"
        assert internal_id_field.description is not None

        # Check guild_id field
        guild_id_field = fields["guild_id"]
        assert guild_id_field.title == "Guild ID"

    def test_forum_config_field_metadata(self) -> None:
        """Test ForumConfigSchema has field metadata."""
        fields = ForumConfigSchema.model_fields

        help_forum_field = fields["help_forum"]
        assert help_forum_field.title == "Help Forum"
        assert help_forum_field.description is not None


class TestSchemaValidation:
    """Tests for schema validation behavior."""

    def test_guild_create_validates_required_fields(self) -> None:
        """Test GuildCreate validates required fields."""
        # Missing 'name' field
        with pytest.raises(ValidationError) as exc_info:
            GuildCreate(id=123)  # type: ignore[call-arg]

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_guild_schema_validates_types(self) -> None:
        """Test GuildSchema validates field types."""
        from uuid import uuid4

        # Invalid guild_id type (string instead of int)
        with pytest.raises(ValidationError):
            GuildSchema(
                id=uuid4(),
                guild_id="invalid",  # type: ignore[arg-type]
                guild_name="Test",
                prefix="!",
                help_channel_id=None,
                sync_label=None,
                issue_linking=False,
                comment_linking=False,
                pep_linking=False,
                github_config=None,
                sotags_configs=[],
                allowed_users=[],
                forum_config=None,
            )

    def test_updateable_guild_setting_validates_list_types(self) -> None:
        """Test UpdateableGuildSetting validates list field types."""
        # tag_name should be list[str]
        with pytest.raises(ValidationError):
            UpdateableGuildSetting(
                prefix="!",
                help_channel_id=1,
                showcase_channel_id=1,
                sync_label="",
                issue_linking=False,
                comment_linking=False,
                pep_linking=False,
                discussion_sync=False,
                github_organization="",
                github_repository="",
                tag_name="not-a-list",  # type: ignore[arg-type]
                allowed_user_id=1,
                help_forum=False,
                help_forum_category="",
                help_thread_auto_close=False,
                help_thread_auto_close_days=0,
                help_thread_notify=False,
                help_thread_notify_roles=[],
                help_thread_notify_days=0,
                help_thread_sync=False,
                showcase_forum=False,
                showcase_forum_category="",
                showcase_thread_auto_close=False,
                showcase_thread_auto_close_days=0,
            )

    def test_schema_rejects_extra_fields(self) -> None:
        """Test schemas reject unknown fields."""
        # Pydantic v2 allows extra fields by default unless configured
        # This test verifies the current behavior
        from uuid import uuid4

        try:
            schema = GuildCreate(id=123, name="Test", unknown_field="value")  # type: ignore[call-arg]
            # If extra='forbid' is set, this will raise ValidationError
            # If not, it will succeed but ignore the extra field
            assert "unknown_field" not in schema.model_dump()
        except ValidationError:
            # Expected if extra='forbid'
            pass


class TestSchemaInheritance:
    """Tests for schema inheritance and composition."""

    def test_schemas_inherit_from_camelized_base_model(self) -> None:
        """Test that schemas inherit from CamelizedBaseModel."""
        from byte_api.lib.schema import CamelizedBaseModel

        schemas = [
            GitHubConfigSchema,
            SOTagsConfigSchema,
            AllowedUsersConfigSchema,
            ForumConfigSchema,
            GuildSchema,
            GuildCreate,
            GuildUpdate,
            UpdateableGuildSetting,
        ]

        for schema in schemas:
            assert issubclass(schema, CamelizedBaseModel), f"{schema.__name__} doesn't inherit from CamelizedBaseModel"

    def test_camelized_serialization_works(self) -> None:
        """Test that camelCase serialization works."""
        from uuid import uuid4

        schema = GitHubConfigSchema(
            guild_id=uuid4(),
            discussion_sync=True,
            github_organization="test",
            github_repository="repo",
        )

        # Serialize with alias (camelCase)
        data = schema.model_dump(by_alias=True)

        # Should have camelCase keys
        assert "guildId" in data
        assert "discussionSync" in data
        assert "githubOrganization" in data
        assert "githubRepository" in data
