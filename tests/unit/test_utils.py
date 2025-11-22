"""Unit tests for utility functions."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from byte_common.utils.encoding import encode_to_base64
from byte_common.utils.strings import camel_case, case_insensitive_string_compare, slugify


class TestSlugify:
    """Tests for the slugify utility function."""

    def test_slugify_basic(self) -> None:
        """Test basic slugification."""
        assert slugify("Hello World") == "hello-world"
        assert slugify("Test String") == "test-string"

    def test_slugify_with_special_characters(self) -> None:
        """Test slugification removes special characters."""
        assert slugify("Hello@World!") == "helloworld"
        assert slugify("Test#String$") == "teststring"
        assert slugify("Foo & Bar") == "foo-bar"

    def test_slugify_with_multiple_spaces(self) -> None:
        """Test slugification handles multiple spaces."""
        assert slugify("Hello   World") == "hello-world"
        assert slugify("Test  String  Here") == "test-string-here"

    def test_slugify_with_hyphens(self) -> None:
        """Test slugification handles existing hyphens."""
        assert slugify("pre-existing-hyphens") == "pre-existing-hyphens"
        assert slugify("multiple---hyphens") == "multiple-hyphens"

    def test_slugify_strips_leading_trailing(self) -> None:
        """Test slugification strips leading/trailing hyphens."""
        assert slugify("-leading") == "leading"
        assert slugify("trailing-") == "trailing"
        assert slugify("-both-") == "both"
        assert slugify("  spaced  ") == "spaced"

    def test_slugify_with_unicode(self) -> None:
        """Test slugification with unicode characters."""
        # Without allow_unicode, should convert to ascii
        assert slugify("Café") == "cafe"
        assert slugify("naïve") == "naive"

    def test_slugify_allow_unicode(self) -> None:
        """Test slugification preserving unicode."""
        result = slugify("Café", allow_unicode=True)
        assert "café" in result.lower()

    def test_slugify_custom_separator(self) -> None:
        """Test slugification with custom separator."""
        assert slugify("Hello World", separator="_") == "hello_world"
        assert slugify("Test String", separator=".") == "test.string"
        assert slugify("Foo Bar Baz", separator="|") == "foo|bar|baz"

    def test_slugify_empty_string(self) -> None:
        """Test slugification of empty string."""
        assert slugify("") == ""
        assert slugify("   ") == ""

    def test_slugify_only_special_characters(self) -> None:
        """Test slugification of string with only special characters."""
        assert slugify("@#$%^&*()") == ""
        assert slugify("!!!") == ""


class TestCamelCase:
    """Tests for the camel_case utility function."""

    def test_camel_case_basic(self) -> None:
        """Test basic camel case conversion."""
        assert camel_case("hello_world") == "helloWorld"
        assert camel_case("test_string") == "testString"

    def test_camel_case_single_word(self) -> None:
        """Test camel case with single word."""
        assert camel_case("hello") == "hello"
        assert camel_case("test") == "test"

    def test_camel_case_multiple_underscores(self) -> None:
        """Test camel case with multiple underscores."""
        assert camel_case("one_two_three") == "oneTwoThree"
        assert camel_case("first_second_third_fourth") == "firstSecondThirdFourth"

    def test_camel_case_already_camel(self) -> None:
        """Test camel case on already camel-cased string."""
        assert camel_case("alreadyCamel") == "alreadyCamel"  # No underscores, treated as one word

    def test_camel_case_empty_string(self) -> None:
        """Test camel case on empty string."""
        assert camel_case("") == ""

    def test_camel_case_leading_underscore(self) -> None:
        """Test camel case with leading underscore."""
        assert camel_case("_leading") == "Leading"  # First element is empty string

    def test_camel_case_trailing_underscore(self) -> None:
        """Test camel case with trailing underscore."""
        assert camel_case("trailing_") == "trailing"  # Last element is empty string

    def test_camel_case_double_underscore(self) -> None:
        """Test camel case with double underscores."""
        result = camel_case("double__underscore")
        # Split creates empty strings between consecutive underscores
        assert "Underscore" in result


class TestCaseInsensitiveStringCompare:
    """Tests for the case_insensitive_string_compare utility function."""

    def test_compare_identical_strings(self) -> None:
        """Test comparing identical strings."""
        assert case_insensitive_string_compare("hello", "hello") is True
        assert case_insensitive_string_compare("WORLD", "WORLD") is True

    def test_compare_different_cases(self) -> None:
        """Test comparing strings with different cases."""
        assert case_insensitive_string_compare("Hello", "hello") is True
        assert case_insensitive_string_compare("WORLD", "world") is True
        assert case_insensitive_string_compare("TeSt", "test") is True

    def test_compare_with_whitespace(self) -> None:
        """Test comparing strings with whitespace."""
        assert case_insensitive_string_compare("  hello  ", "hello") is True
        assert case_insensitive_string_compare("world", "  world  ") is True
        assert case_insensitive_string_compare("  test  ", "  TEST  ") is True

    def test_compare_different_strings(self) -> None:
        """Test comparing different strings."""
        assert case_insensitive_string_compare("hello", "world") is False
        assert case_insensitive_string_compare("test", "TEST2") is False

    def test_compare_empty_strings(self) -> None:
        """Test comparing empty strings."""
        assert case_insensitive_string_compare("", "") is True
        assert case_insensitive_string_compare("   ", "  ") is True

    def test_compare_empty_with_non_empty(self) -> None:
        """Test comparing empty with non-empty strings."""
        assert case_insensitive_string_compare("", "hello") is False
        assert case_insensitive_string_compare("world", "") is False

    def test_compare_with_special_characters(self) -> None:
        """Test comparing strings with special characters."""
        assert case_insensitive_string_compare("hello@world", "HELLO@WORLD") is True
        assert case_insensitive_string_compare("test#123", "TEST#123") is True


class TestEncodeToBase64:
    """Tests for the encode_to_base64 utility function."""

    def test_encode_text_file(self) -> None:
        """Test encoding a text file to base64."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Hello, World!")
            temp_path = Path(f.name)

        try:
            encoded = encode_to_base64(temp_path)
            assert isinstance(encoded, str)
            assert len(encoded) > 0

            # Verify it's valid base64 by decoding
            import base64

            decoded = base64.b64decode(encoded).decode("utf-8")
            assert decoded == "Hello, World!"
        finally:
            temp_path.unlink()

    def test_encode_binary_file(self) -> None:
        """Test encoding a binary file to base64."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".bin") as f:
            f.write(b"\x00\x01\x02\x03\xff\xfe")
            temp_path = Path(f.name)

        try:
            encoded = encode_to_base64(temp_path)
            assert isinstance(encoded, str)
            assert len(encoded) > 0

            # Verify it's valid base64 by decoding
            import base64

            decoded = base64.b64decode(encoded)
            assert decoded == b"\x00\x01\x02\x03\xff\xfe"
        finally:
            temp_path.unlink()

    def test_encode_empty_file(self) -> None:
        """Test encoding an empty file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_path = Path(f.name)

        try:
            encoded = encode_to_base64(temp_path)
            assert isinstance(encoded, str)
            assert encoded == ""  # Empty file should encode to empty string
        finally:
            temp_path.unlink()

    def test_encode_nonexistent_file(self) -> None:
        """Test encoding a nonexistent file raises error."""
        nonexistent = Path("/tmp/nonexistent_file_12345.txt")
        with pytest.raises(FileNotFoundError):
            encode_to_base64(nonexistent)

    def test_encode_unicode_content(self) -> None:
        """Test encoding a file with unicode content."""
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".txt") as f:
            f.write("Hello 世界 🌍")
            temp_path = Path(f.name)

        try:
            encoded = encode_to_base64(temp_path)
            assert isinstance(encoded, str)

            # Verify it's valid base64 by decoding
            import base64

            decoded = base64.b64decode(encoded).decode("utf-8")
            assert decoded == "Hello 世界 🌍"
        finally:
            temp_path.unlink()
