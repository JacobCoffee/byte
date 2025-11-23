"""Tests for serialization helpers."""

from __future__ import annotations

import datetime
from json import dumps as json_dumps
from uuid import uuid4

import pytest
from pydantic import BaseModel

from byte_api.lib.serialization import (
    UUIDEncoder,
    convert_camel_to_snake_case,
    convert_datetime_to_gmt,
    convert_string_to_camel_case,
    from_json,
    from_msgpack,
    to_json,
    to_msgpack,
)

__all__ = [
    "TestCaseConversion",
    "TestDatetimeConversion",
    "TestJSONSerialization",
    "TestMsgPackSerialization",
    "TestUUIDEncoder",
]


class TestJSONSerialization:
    """Tests for JSON encoding/decoding."""

    def test_to_json_simple_dict(self) -> None:
        """Test encoding a simple dictionary to JSON."""
        data = {"key": "value", "number": 42}
        result = to_json(data)

        assert isinstance(result, bytes)
        assert b"key" in result
        assert b"value" in result
        assert b"42" in result

    def test_from_json_simple_dict(self) -> None:
        """Test decoding JSON bytes to dictionary."""
        json_bytes = b'{"key": "value", "number": 42}'
        result = from_json(json_bytes)

        assert result == {"key": "value", "number": 42}

    def test_from_json_string_input(self) -> None:
        """Test decoding JSON string to dictionary."""
        json_str = '{"key": "value"}'
        result = from_json(json_str)

        assert result == {"key": "value"}

    def test_to_json_nested_structure(self) -> None:
        """Test encoding nested data structures."""
        data = {
            "level1": {"level2": {"level3": "deep"}},
            "array": [1, 2, 3],
        }
        result = to_json(data)

        assert isinstance(result, bytes)
        assert b"level1" in result
        assert b"deep" in result

    def test_roundtrip_json(self) -> None:
        """Test JSON encode/decode roundtrip."""
        original = {"test": "data", "nested": {"value": 123}}
        encoded = to_json(original)
        decoded = from_json(encoded)

        assert decoded == original

    def test_to_json_with_pydantic_model(self) -> None:
        """Test encoding Pydantic model to JSON."""

        class TestModel(BaseModel):
            name: str
            value: int

        model = TestModel(name="test", value=42)
        result = to_json({"model": model})

        assert isinstance(result, bytes)

    def test_to_json_handles_encoding_error(self) -> None:
        """Test that encoding errors are handled gracefully."""

        class UnserializableClass:
            def __str__(self):
                raise RuntimeError("Cannot serialize")

        # The _default encoder will catch this and raise TypeError
        with pytest.raises(TypeError):
            to_json({"obj": UnserializableClass()})


class TestMsgPackSerialization:
    """Tests for MessagePack encoding/decoding."""

    def test_to_msgpack_simple_dict(self) -> None:
        """Test encoding a simple dictionary to MessagePack."""
        data = {"key": "value", "number": 42}
        result = to_msgpack(data)

        assert isinstance(result, bytes)

    def test_from_msgpack_simple_dict(self) -> None:
        """Test decoding MessagePack bytes to dictionary."""
        data = {"key": "value", "number": 42}
        packed = to_msgpack(data)
        result = from_msgpack(packed)

        assert result == data

    def test_roundtrip_msgpack(self) -> None:
        """Test MessagePack encode/decode roundtrip."""
        original = {"test": "data", "nested": {"value": 123}, "array": [1, 2, 3]}
        encoded = to_msgpack(original)
        decoded = from_msgpack(encoded)

        assert decoded == original

    def test_to_msgpack_with_pydantic_model(self) -> None:
        """Test encoding Pydantic model to MessagePack."""

        class TestModel(BaseModel):
            name: str
            value: int

        model = TestModel(name="test", value=42)
        result = to_msgpack({"model": model})

        assert isinstance(result, bytes)


class TestDatetimeConversion:
    """Tests for datetime conversion functions."""

    def test_convert_datetime_to_gmt_with_utc(self) -> None:
        """Test converting UTC datetime to GMT string."""
        dt = datetime.datetime(2024, 1, 15, 12, 30, 45, tzinfo=datetime.UTC)
        result = convert_datetime_to_gmt(dt)

        assert result == "2024-01-15T12:30:45Z"
        assert result.endswith("Z")
        assert "+00:00" not in result

    def test_convert_datetime_to_gmt_without_timezone(self) -> None:
        """Test converting naive datetime (assumes UTC)."""
        dt = datetime.datetime(2024, 1, 15, 12, 30, 45)
        result = convert_datetime_to_gmt(dt)

        assert result == "2024-01-15T12:30:45Z"
        assert result.endswith("Z")

    def test_convert_datetime_to_gmt_with_other_timezone(self) -> None:
        """Test converting datetime with non-UTC timezone."""
        # Create a timezone-aware datetime
        from datetime import timedelta, timezone

        tz = timezone(timedelta(hours=5))
        dt = datetime.datetime(2024, 1, 15, 12, 30, 45, tzinfo=tz)
        result = convert_datetime_to_gmt(dt)

        # Should preserve the timezone in ISO format
        assert "2024-01-15T12:30:45" in result
        assert isinstance(result, str)


class TestCaseConversion:
    """Tests for string case conversion functions."""

    def test_convert_string_to_camel_case_simple(self) -> None:
        """Test converting snake_case to camelCase."""
        assert convert_string_to_camel_case("hello_world") == "helloWorld"

    def test_convert_string_to_camel_case_multiple_words(self) -> None:
        """Test converting multi-word snake_case to camelCase."""
        assert convert_string_to_camel_case("this_is_a_test") == "thisIsATest"

    def test_convert_string_to_camel_case_single_word(self) -> None:
        """Test converting single word (no change expected)."""
        assert convert_string_to_camel_case("hello") == "hello"

    def test_convert_string_to_camel_case_already_camel(self) -> None:
        """Test converting already camelCase string (no underscores)."""
        assert convert_string_to_camel_case("helloWorld") == "helloWorld"

    def test_convert_camel_to_snake_case_simple(self) -> None:
        """Test converting camelCase to snake_case."""
        assert convert_camel_to_snake_case("helloWorld") == "hello_world"

    def test_convert_camel_to_snake_case_multiple_words(self) -> None:
        """Test converting multi-word camelCase to snake_case."""
        assert convert_camel_to_snake_case("thisIsATest") == "this_is_a_test"

    def test_convert_camel_to_snake_case_single_word(self) -> None:
        """Test converting single lowercase word (no change)."""
        assert convert_camel_to_snake_case("hello") == "hello"

    def test_convert_camel_to_snake_case_already_snake(self) -> None:
        """Test converting already snake_case string."""
        # Note: This will add underscores before capitals if any exist
        assert convert_camel_to_snake_case("hello_world") == "hello_world"

    def test_roundtrip_case_conversion(self) -> None:
        """Test snake -> camel -> snake conversion."""
        original = "test_string_value"
        camel = convert_string_to_camel_case(original)
        back_to_snake = convert_camel_to_snake_case(camel)

        assert back_to_snake == original


class TestUUIDEncoder:
    """Tests for UUIDEncoder JSON encoder."""

    def test_uuid_encoder_with_uuid(self) -> None:
        """Test encoding UUID objects."""
        test_uuid = uuid4()

        result = json_dumps({"id": test_uuid}, cls=UUIDEncoder)

        assert str(test_uuid) in result
        assert isinstance(result, str)

    def test_uuid_encoder_with_non_uuid(self) -> None:
        """Test encoding non-UUID objects (delegates to default)."""
        # Should work with standard types
        result = json_dumps({"value": 42, "text": "hello"}, cls=UUIDEncoder)

        assert "42" in result
        assert "hello" in result

    def test_uuid_encoder_default_method(self) -> None:
        """Test UUIDEncoder.default() method directly."""
        encoder = UUIDEncoder()
        test_uuid = uuid4()

        result = encoder.default(test_uuid)

        assert result == str(test_uuid)
        assert isinstance(result, str)

    def test_uuid_encoder_complex_structure(self) -> None:
        """Test encoding complex structure with UUIDs."""
        uuid1 = uuid4()
        uuid2 = uuid4()

        data = {
            "primary_id": uuid1,
            "nested": {"secondary_id": uuid2, "value": 123},
        }

        result = json_dumps(data, cls=UUIDEncoder)

        assert str(uuid1) in result
        assert str(uuid2) in result
        assert "123" in result
