"""Unit tests for Pydantic schemas."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from byte_common.schemas.guild import CreateGuildRequest, GuildSchema, UpdateGuildRequest

if TYPE_CHECKING:
    from byte_common.models.guild import Guild


class TestGuildSchema:
    """Tests for GuildSchema."""

    def test_guild_schema_from_model(self, sample_guild: Guild) -> None:
        """Test creating GuildSchema from Guild model."""
        schema = GuildSchema.model_validate(sample_guild)

        assert schema.id == sample_guild.id
        assert schema.guild_id == sample_guild.guild_id
        assert schema.guild_name == sample_guild.guild_name
        assert schema.prefix == sample_guild.prefix
        assert schema.help_channel_id == sample_guild.help_channel_id
        assert schema.showcase_channel_id == sample_guild.showcase_channel_id
        assert schema.sync_label == sample_guild.sync_label
        assert schema.issue_linking == sample_guild.issue_linking
        assert schema.comment_linking == sample_guild.comment_linking
        assert schema.pep_linking == sample_guild.pep_linking

    def test_guild_schema_serialization(self) -> None:
        """Test GuildSchema serialization to dict."""
        guild_id = uuid4()
        schema = GuildSchema(
            id=guild_id,
            guild_id=123456789012345678,
            guild_name="Test Guild",
            prefix="!",
        )

        data = schema.model_dump()

        assert data["id"] == guild_id
        assert data["guild_id"] == 123456789012345678
        assert data["guild_name"] == "Test Guild"
        assert data["prefix"] == "!"
        assert data["issue_linking"] is False
        assert data["comment_linking"] is False
        assert data["pep_linking"] is False

    def test_guild_schema_defaults(self) -> None:
        """Test GuildSchema default values."""
        schema = GuildSchema(
            id=uuid4(),
            guild_id=123456789012345678,
            guild_name="Test Guild",
        )

        assert schema.prefix == "!"
        assert schema.help_channel_id is None
        assert schema.showcase_channel_id is None
        assert schema.sync_label is None
        assert schema.issue_linking is False
        assert schema.comment_linking is False
        assert schema.pep_linking is False


class TestCreateGuildRequest:
    """Tests for CreateGuildRequest schema."""

    def test_create_guild_request_valid(self) -> None:
        """Test creating a valid CreateGuildRequest."""
        request = CreateGuildRequest(
            guild_id=123456789012345678,
            guild_name="Test Guild",
            prefix="$",
            issue_linking=True,
        )

        assert request.guild_id == 123456789012345678
        assert request.guild_name == "Test Guild"
        assert request.prefix == "$"
        assert request.issue_linking is True
        assert request.comment_linking is False  # Default

    def test_create_guild_request_defaults(self) -> None:
        """Test CreateGuildRequest default values."""
        request = CreateGuildRequest(
            guild_id=123456789012345678,
            guild_name="Test Guild",
        )

        assert request.prefix == "!"
        assert request.help_channel_id is None
        assert request.showcase_channel_id is None
        assert request.sync_label is None
        assert request.issue_linking is False
        assert request.comment_linking is False
        assert request.pep_linking is False

    def test_create_guild_request_missing_required_fields(self) -> None:
        """Test that required fields are validated."""
        with pytest.raises(ValidationError) as exc_info:
            CreateGuildRequest(guild_name="Test Guild")  # Missing guild_id

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("guild_id",) for error in errors)

    def test_create_guild_request_guild_name_validation(self) -> None:
        """Test guild_name length validation."""
        # Empty string should fail
        with pytest.raises(ValidationError) as exc_info:
            CreateGuildRequest(
                guild_id=123456789012345678,
                guild_name="",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("guild_name",) for error in errors)

        # String too long should fail (>100 chars)
        with pytest.raises(ValidationError):
            CreateGuildRequest(
                guild_id=123456789012345678,
                guild_name="x" * 101,
            )

    def test_create_guild_request_prefix_validation(self) -> None:
        """Test prefix length validation."""
        # Empty prefix should fail
        with pytest.raises(ValidationError):
            CreateGuildRequest(
                guild_id=123456789012345678,
                guild_name="Test Guild",
                prefix="",
            )

        # Prefix too long should fail (>5 chars)
        with pytest.raises(ValidationError):
            CreateGuildRequest(
                guild_id=123456789012345678,
                guild_name="Test Guild",
                prefix="!!!!!!",
            )

    def test_create_guild_request_optional_fields(self) -> None:
        """Test optional fields can be set."""
        request = CreateGuildRequest(
            guild_id=123456789012345678,
            guild_name="Test Guild",
            help_channel_id=111111111111111111,
            showcase_channel_id=222222222222222222,
            sync_label="sync",
        )

        assert request.help_channel_id == 111111111111111111
        assert request.showcase_channel_id == 222222222222222222
        assert request.sync_label == "sync"


class TestUpdateGuildRequest:
    """Tests for UpdateGuildRequest schema."""

    def test_update_guild_request_partial_update(self) -> None:
        """Test partial update with UpdateGuildRequest."""
        request = UpdateGuildRequest(
            guild_name="Updated Guild",
            issue_linking=True,
        )

        assert request.guild_name == "Updated Guild"
        assert request.issue_linking is True
        # Other fields should be None (not provided)
        assert request.prefix is None
        assert request.comment_linking is None

    def test_update_guild_request_all_none(self) -> None:
        """Test UpdateGuildRequest with no fields set."""
        request = UpdateGuildRequest()

        assert request.guild_name is None
        assert request.prefix is None
        assert request.help_channel_id is None
        assert request.showcase_channel_id is None
        assert request.sync_label is None
        assert request.issue_linking is None
        assert request.comment_linking is None
        assert request.pep_linking is None

    def test_update_guild_request_guild_name_validation(self) -> None:
        """Test guild_name validation on update."""
        # Empty string should fail
        with pytest.raises(ValidationError):
            UpdateGuildRequest(guild_name="")

        # Too long should fail
        with pytest.raises(ValidationError):
            UpdateGuildRequest(guild_name="x" * 101)

    def test_update_guild_request_prefix_validation(self) -> None:
        """Test prefix validation on update."""
        # Empty prefix should fail
        with pytest.raises(ValidationError):
            UpdateGuildRequest(prefix="")

        # Too long should fail
        with pytest.raises(ValidationError):
            UpdateGuildRequest(prefix="!!!!!!")

    def test_update_guild_request_serialization(self) -> None:
        """Test serialization excludes None values."""
        request = UpdateGuildRequest(
            guild_name="Updated",
            issue_linking=True,
        )

        data = request.model_dump(exclude_none=True)

        assert "guild_name" in data
        assert "issue_linking" in data
        assert "prefix" not in data
        assert "comment_linking" not in data
