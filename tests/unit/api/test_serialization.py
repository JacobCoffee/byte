"""Tests for serialization helpers."""

from __future__ import annotations

import datetime
import importlib.util
import sys
from json import dumps as json_dumps
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import BaseModel

# Import the serialization module directly without triggering __init__.py
serialization_path = (
    Path(__file__).parent.parent.parent.parent / "services" / "api" / "src" / "byte_api" / "lib" / "serialization.py"
)
spec = importlib.util.spec_from_file_location("serialization", serialization_path)
serialization = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules["serialization"] = serialization
spec.loader.exec_module(serialization)  # type: ignore[union-attr]

UUIDEncoder = serialization.UUIDEncoder
convert_camel_to_snake_case = serialization.convert_camel_to_snake_case
convert_datetime_to_gmt = serialization.convert_datetime_to_gmt
convert_string_to_camel_case = serialization.convert_string_to_camel_case
from_json = serialization.from_json
from_msgpack = serialization.from_msgpack
to_json = serialization.to_json
to_msgpack = serialization.to_msgpack

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

    def test_to_json_with_custom_stringifiable_object(self) -> None:
        """Test encoding custom object with __str__ method."""

        class CustomObject:
            def __str__(self):
                return "custom_value"

        result = to_json({"obj": CustomObject()})
        assert isinstance(result, bytes)
        # The object should be stringified
        assert b"custom_value" in result

    def test_to_json_handles_encoding_error(self) -> None:
        """Test that encoding errors are handled gracefully."""

        class UnserializableClass:
            def __str__(self):
                raise RuntimeError("Cannot serialize")

        # The _default encoder will catch this and raise TypeError
        with pytest.raises(TypeError):
            to_json({"obj": UnserializableClass()})

    def test_to_json_with_deeply_nested_structures(self) -> None:
        """Test encoding deeply nested dict/list structures."""
        nested = {"a": {"b": {"c": {"d": {"e": "deep"}}}}}
        result = to_json(nested)

        assert isinstance(result, bytes)
        decoded = from_json(result)
        assert decoded["a"]["b"]["c"]["d"]["e"] == "deep"

    def test_to_json_with_mixed_nested_types(self) -> None:
        """Test encoding mixed nested structures with lists and dicts."""
        data = {
            "lists": [[1, 2, 3], [4, 5, 6]],
            "nested_dicts": {"a": {"b": [1, 2, {"c": 3}]}},
            "mixed": [{"key": "value"}, [1, 2, 3], "string"],
        }
        result = to_json(data)

        assert isinstance(result, bytes)
        decoded = from_json(result)
        assert decoded == data

    def test_to_json_with_empty_structures(self) -> None:
        """Test encoding empty dicts and lists."""
        data = {"empty_dict": {}, "empty_list": [], "nested_empty": {"a": []}}
        result = to_json(data)

        decoded = from_json(result)
        assert decoded == data

    def test_to_json_with_special_characters(self) -> None:
        """Test encoding strings with special characters."""
        data = {
            "unicode": "Hello 世界 🌍",
            "quotes": 'He said "hello"',
            "newlines": "line1\nline2\nline3",
            "tabs": "col1\tcol2\tcol3",
        }
        result = to_json(data)

        decoded = from_json(result)
        assert decoded == data

    def test_to_json_with_boolean_and_null(self) -> None:
        """Test encoding boolean and null values."""
        data = {"true_val": True, "false_val": False, "null_val": None}
        result = to_json(data)

        decoded = from_json(result)
        assert decoded == data

    def test_to_json_with_large_numbers(self) -> None:
        """Test encoding very large numbers."""
        data = {
            "large_int": 9999999999999999999999999999,
            "negative_int": -9999999999999999999999999999,
            "float": 1.23456789012345,
        }
        result = to_json(data)

        decoded = from_json(result)
        assert decoded == data


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

    def test_to_msgpack_with_binary_data(self) -> None:
        """Test encoding binary data in MessagePack."""
        data = {"binary": b"binary data", "text": "text data"}
        result = to_msgpack(data)

        assert isinstance(result, bytes)
        decoded = from_msgpack(result)
        assert decoded == data

    def test_to_msgpack_with_deeply_nested_structures(self) -> None:
        """Test MessagePack with deeply nested structures."""
        nested = {"a": {"b": {"c": {"d": [1, 2, 3]}}}}
        result = to_msgpack(nested)

        decoded = from_msgpack(result)
        assert decoded == nested

    def test_to_msgpack_with_empty_structures(self) -> None:
        """Test MessagePack with empty dicts and lists."""
        data = {"empty": {}, "list": [], "nested": {"a": []}}
        result = to_msgpack(data)

        decoded = from_msgpack(result)
        assert decoded == data

    def test_to_msgpack_with_special_characters(self) -> None:
        """Test MessagePack with unicode and special characters."""
        data = {"unicode": "Hello 世界 🌍", "special": "line1\nline2\ttab"}
        result = to_msgpack(data)

        decoded = from_msgpack(result)
        assert decoded == data

    def test_msgpack_handles_encoding_error(self) -> None:
        """Test that MessagePack encoding errors are handled gracefully."""

        class UnserializableClass:
            def __str__(self):
                raise RuntimeError("Cannot serialize")

        with pytest.raises(TypeError):
            to_msgpack({"obj": UnserializableClass()})


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

    def test_convert_datetime_to_gmt_with_microseconds(self) -> None:
        """Test converting datetime with microseconds."""
        dt = datetime.datetime(2024, 1, 15, 12, 30, 45, 123456, tzinfo=datetime.UTC)
        result = convert_datetime_to_gmt(dt)

        assert "2024-01-15T12:30:45.123456Z" in result
        assert result.endswith("Z")

    def test_convert_datetime_to_gmt_with_negative_timezone(self) -> None:
        """Test converting datetime with negative timezone offset."""
        from datetime import timedelta, timezone

        tz = timezone(timedelta(hours=-5))
        dt = datetime.datetime(2024, 1, 15, 12, 30, 45, tzinfo=tz)
        result = convert_datetime_to_gmt(dt)

        assert "2024-01-15T12:30:45" in result
        assert "-05:00" in result

    def test_convert_datetime_to_gmt_naive_midnight(self) -> None:
        """Test converting naive datetime at midnight."""
        dt = datetime.datetime(2024, 1, 15, 0, 0, 0)
        result = convert_datetime_to_gmt(dt)

        assert result == "2024-01-15T00:00:00Z"


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

    def test_convert_string_to_camel_case_with_numbers(self) -> None:
        """Test converting snake_case with numbers to camelCase."""
        assert convert_string_to_camel_case("var_1_test") == "var1Test"
        assert convert_string_to_camel_case("http_2_protocol") == "http2Protocol"

    def test_convert_string_to_camel_case_empty_string(self) -> None:
        """Test converting empty string."""
        assert convert_string_to_camel_case("") == ""

    def test_convert_string_to_camel_case_consecutive_underscores(self) -> None:
        """Test converting string with consecutive underscores."""
        assert convert_string_to_camel_case("hello__world") == "helloWorld"

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

    def test_convert_camel_to_snake_case_with_acronyms(self) -> None:
        """Test converting camelCase with acronyms to snake_case."""
        # First char stays as-is, rest of uppercase chars get underscore+lowercase
        assert convert_camel_to_snake_case("HTTPSConnection") == "H_t_t_p_s_connection"
        assert convert_camel_to_snake_case("XMLParser") == "X_m_l_parser"
        assert convert_camel_to_snake_case("parseXML") == "parse_x_m_l"

    def test_convert_camel_to_snake_case_with_numbers(self) -> None:
        """Test converting camelCase with numbers to snake_case."""
        assert convert_camel_to_snake_case("variable1Test") == "variable1_test"

    def test_convert_camel_to_snake_case_consecutive_capitals(self) -> None:
        """Test converting consecutive capital letters."""
        # First char stays uppercase
        assert convert_camel_to_snake_case("IOError") == "I_o_error"

    def test_convert_camel_to_snake_case_empty_string(self) -> None:
        """Test converting empty string."""
        assert convert_camel_to_snake_case("") == ""

    def test_convert_camel_to_snake_case_starts_with_capital(self) -> None:
        """Test converting PascalCase to snake_case."""
        # First char stays uppercase
        assert convert_camel_to_snake_case("HelloWorld") == "Hello_world"

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

    def test_uuid_encoder_raises_for_unserializable(self) -> None:
        """Test UUIDEncoder raises TypeError for unserializable non-UUID objects."""
        encoder = UUIDEncoder()

        # Create an unserializable object
        class UnserializableObject:
            pass

        with pytest.raises(TypeError):
            encoder.default(UnserializableObject())
