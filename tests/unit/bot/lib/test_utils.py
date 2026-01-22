"""Tests for utils module."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import Mock, patch

import httpx
import pytest

from byte_bot.lib.types.astral import RuffRule
from byte_bot.lib.types.python import PEPStatus, PEPType
from byte_bot.lib.utils import (
    chunk_sequence,
    format_resolution_link,
    format_ruff_rule,
    get_next_friday,
    linker,
    paste,
    query_all_peps,
    query_all_ruff_rules,
    run_ruff_format,
    smart_chunk_text,
)


class TestLinker:
    """Tests for linker function."""

    def test_linker_with_embed(self) -> None:
        """Test linker with embed enabled."""
        result = linker("Test Title", "https://example.com", show_embed=True)
        assert result == "[Test Title](https://example.com)"

    def test_linker_without_embed(self) -> None:
        """Test linker without embed (default)."""
        result = linker("Test Title", "https://example.com", show_embed=False)
        assert result == "[Test Title](<https://example.com>)"

    def test_linker_default_embed(self) -> None:
        """Test linker with default show_embed parameter."""
        result = linker("Test Title", "https://example.com")
        assert result == "[Test Title](<https://example.com>)"

    def test_linker_special_characters(self) -> None:
        """Test linker with special characters in title."""
        result = linker("Test (Title)", "https://example.com/path?query=1")
        assert result == "[Test (Title)](<https://example.com/path?query=1>)"

    def test_linker_empty_title(self) -> None:
        """Test linker with empty title."""
        result = linker("", "https://example.com")
        assert result == "[](<https://example.com>)"

    def test_linker_unicode_title(self) -> None:
        """Test linker with unicode characters in title."""
        result = linker("テスト", "https://example.com")
        assert result == "[テスト](<https://example.com>)"

    def test_linker_markdown_in_title(self) -> None:
        """Test linker with markdown characters in title."""
        result = linker("Test [Title]", "https://example.com")
        assert result == "[Test [Title]](<https://example.com>)"


class TestFormatRuffRule:
    """Tests for format_ruff_rule function."""

    def test_format_ruff_rule_complete(self) -> None:
        """Test formatting a complete ruff rule."""
        rule_data: RuffRule = {
            "code": "E501",
            "name": "line-too-long",
            "summary": "Line too long",
            "explanation": "## Why this is bad\nLong lines are hard to read.",
            "fix": "Break the line",
            "linter": "pycodestyle",
            "message_formats": ["Line too long ({width} > {limit})"],
            "preview": False,
        }

        result = format_ruff_rule(rule_data)

        assert result["name"] == "line-too-long"
        assert result["summary"] == "Line too long"
        assert "**Why this is bad**" in result["explanation"]
        assert result["fix"] == "Break the line"
        assert result["rule_link"] == "https://docs.astral.sh/ruff/rules/line-too-long"
        assert result["rule_anchor_link"] == "https://docs.astral.sh/ruff/rules/#E501"

    def test_format_ruff_rule_multiple_headers(self) -> None:
        """Test formatting explanation with multiple markdown headers."""
        rule_data: RuffRule = {
            "code": "F401",
            "name": "unused-import",
            "summary": "Unused import",
            "explanation": "## Why this is bad\nUnused imports clutter.\n## How to fix\nRemove them.",
            "fix": "Remove import",
            "linter": "pyflakes",
            "message_formats": [],
            "preview": False,
        }

        result = format_ruff_rule(rule_data)

        assert "**Why this is bad**" in result["explanation"]
        assert "**How to fix**" in result["explanation"]

    def test_format_ruff_rule_minimal_explanation(self) -> None:
        """Test formatting rule with minimal explanation."""
        rule_data: RuffRule = {
            "code": "E501",
            "name": "line-too-long",
            "summary": "Line too long",
            "explanation": "Simple explanation without headers",
            "fix": "Break the line",
            "linter": "pycodestyle",
            "message_formats": [],
            "preview": False,
        }

        result = format_ruff_rule(rule_data)

        assert result["name"] == "line-too-long"
        assert result["explanation"] == "Simple explanation without headers"

    def test_format_ruff_rule_missing_optional_fields(self) -> None:
        """Test formatting rule with missing optional fields uses defaults."""
        rule_data: RuffRule = {
            "code": "E999",
            "name": "syntax-error",
            # Missing: summary, fix (explanation is required)
            "explanation": "Syntax errors detected",
            "linter": "pyflakes",
            "message_formats": [],
            "preview": False,
        }

        result = format_ruff_rule(rule_data)

        assert result["name"] == "syntax-error"
        assert result["summary"] == "No summary available"
        assert "Syntax errors detected" in result["explanation"]
        assert result["fix"] == "No fix available"

    def test_format_ruff_rule_empty_explanation(self) -> None:
        """Test formatting rule with empty explanation."""
        rule_data: RuffRule = {
            "code": "E501",
            "name": "line-too-long",
            "summary": "Line too long",
            "explanation": "",
            "fix": "Break the line",
            "linter": "pycodestyle",
            "message_formats": [],
            "preview": False,
        }

        result = format_ruff_rule(rule_data)

        assert result["explanation"] == ""

    def test_format_ruff_rule_complex_headers(self) -> None:
        """Test formatting rule with complex header patterns."""
        rule_data: RuffRule = {
            "code": "F401",
            "name": "unused-import",
            "summary": "Unused import",
            "explanation": (
                "## Why this is bad\nBad imports.\n\n## How to fix it\nRemove.\n\n## Edge cases\nSome cases."
            ),
            "fix": "Remove import",
            "linter": "pyflakes",
            "message_formats": [],
            "preview": False,
        }

        result = format_ruff_rule(rule_data)

        assert "**Why this is bad**" in result["explanation"]
        assert "**How to fix it**" in result["explanation"]
        assert "**Edge cases**" in result["explanation"]


class TestQueryAllRuffRules:
    """Tests for query_all_ruff_rules function."""

    @pytest.mark.asyncio
    async def test_query_all_ruff_rules_success(self) -> None:
        """Test successful query of all ruff rules."""
        mock_rules = [
            {
                "code": "E501",
                "name": "line-too-long",
                "summary": "Line too long",
                "explanation": "Long lines are bad",
                "fix": "Break the line",
                "linter": "pycodestyle",
                "message_formats": [],
                "preview": False,
            }
        ]

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(mock_rules).encode()

        with (
            patch("byte_bot.lib.utils.find_ruff_bin", return_value="/usr/bin/ruff"),
            patch("byte_bot.lib.utils.run_process", return_value=mock_result),
        ):
            rules = await query_all_ruff_rules()

            assert len(rules) == 1
            assert rules[0]["code"] == "E501"
            assert rules[0]["name"] == "line-too-long"

    @pytest.mark.asyncio
    async def test_query_all_ruff_rules_failure(self) -> None:
        """Test query failure with non-zero return code."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = b"Command failed"

        with (
            patch("byte_bot.lib.utils.find_ruff_bin", return_value="/usr/bin/ruff"),
            patch("byte_bot.lib.utils.run_process", return_value=mock_result),
        ):
            with pytest.raises(ValueError, match="Error while querying all rules"):
                await query_all_ruff_rules()

    @pytest.mark.asyncio
    async def test_query_all_ruff_rules_empty_stderr(self) -> None:
        """Test query failure with empty stderr."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = None

        with (
            patch("byte_bot.lib.utils.find_ruff_bin", return_value="/usr/bin/ruff"),
            patch("byte_bot.lib.utils.run_process", return_value=mock_result),
        ):
            with pytest.raises(ValueError, match="Error while querying all rules"):
                await query_all_ruff_rules()

    @pytest.mark.asyncio
    async def test_query_all_ruff_rules_empty_list(self) -> None:
        """Test query returning empty list of rules."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = b"[]"

        with (
            patch("byte_bot.lib.utils.find_ruff_bin", return_value="/usr/bin/ruff"),
            patch("byte_bot.lib.utils.run_process", return_value=mock_result),
        ):
            rules = await query_all_ruff_rules()

            assert len(rules) == 0

    @pytest.mark.asyncio
    async def test_query_all_ruff_rules_multiple_rules(self) -> None:
        """Test query returning multiple rules."""
        mock_rules = [
            {
                "code": "E501",
                "name": "line-too-long",
                "summary": "Line too long",
                "explanation": "Long lines are bad",
                "fix": "Break the line",
                "linter": "pycodestyle",
                "message_formats": [],
                "preview": False,
            },
            {
                "code": "F401",
                "name": "unused-import",
                "summary": "Unused import",
                "explanation": "Remove unused imports",
                "fix": "Remove import",
                "linter": "pyflakes",
                "message_formats": [],
                "preview": False,
            },
        ]

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(mock_rules).encode()

        with (
            patch("byte_bot.lib.utils.find_ruff_bin", return_value="/usr/bin/ruff"),
            patch("byte_bot.lib.utils.run_process", return_value=mock_result),
        ):
            rules = await query_all_ruff_rules()

            assert len(rules) == 2
            codes = [rule["code"] for rule in rules]
            assert "E501" in codes
            assert "F401" in codes

    @pytest.mark.asyncio
    async def test_query_all_ruff_rules_invalid_json(self) -> None:
        """Test query with invalid JSON response."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = b"invalid json"

        with (
            patch("byte_bot.lib.utils.find_ruff_bin", return_value="/usr/bin/ruff"),
            patch("byte_bot.lib.utils.run_process", return_value=mock_result),
        ):
            with pytest.raises(json.JSONDecodeError):
                await query_all_ruff_rules()


class TestRunRuffFormat:
    """Tests for run_ruff_format function."""

    def test_run_ruff_format_success(self) -> None:
        """Test successful ruff format."""
        code = "x=1"
        formatted_code = "x = 1\n"

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = formatted_code

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = run_ruff_format(code)

            assert result == formatted_code
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0] == ["ruff", "format", "-"]
            assert call_args[1]["input"] == code
            assert call_args[1]["capture_output"] is True
            assert call_args[1]["text"] is True
            assert call_args[1]["check"] is False

    def test_run_ruff_format_failure_returns_original(self) -> None:
        """Test ruff format failure returns original code."""
        code = "x=1"

        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            result = run_ruff_format(code)

            assert result == code

    def test_run_ruff_format_multiline_code(self) -> None:
        """Test ruff format with multiline code."""
        code = "def foo():\n    x=1\n    return x"
        formatted_code = "def foo():\n    x = 1\n    return x\n"

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = formatted_code

        with patch("subprocess.run", return_value=mock_result):
            result = run_ruff_format(code)

            assert result == formatted_code

    def test_run_ruff_format_empty_code(self) -> None:
        """Test ruff format with empty code."""
        code = ""
        formatted_code = ""

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = formatted_code

        with patch("subprocess.run", return_value=mock_result):
            result = run_ruff_format(code)

            assert result == formatted_code

    def test_run_ruff_format_subprocess_exception(self) -> None:
        """Test ruff format when subprocess raises exception."""
        code = "x=1"

        with patch("subprocess.run", side_effect=FileNotFoundError("ruff not found")):
            with pytest.raises(FileNotFoundError):
                run_ruff_format(code)

    def test_run_ruff_format_unicode_code(self) -> None:
        """Test ruff format with unicode characters."""
        code = "x = 'こんにちは'"
        formatted_code = "x = 'こんにちは'\n"

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = formatted_code

        with patch("subprocess.run", return_value=mock_result):
            result = run_ruff_format(code)

            assert result == formatted_code


class TestPaste:
    """Tests for paste function."""

    @pytest.mark.asyncio
    async def test_paste_success(self, respx_mock) -> None:
        """Test successful paste upload."""
        code = "print('hello')"
        paste_link = "https://paste.pythondiscord.com/abc123"

        respx_mock.post("https://paste.pythondiscord.com/api/v1/paste").mock(
            return_value=httpx.Response(200, json={"link": paste_link})
        )

        result = await paste(code)

        assert result == paste_link

    @pytest.mark.asyncio
    async def test_paste_no_link_in_response(self, respx_mock) -> None:
        """Test paste with missing link in response."""
        code = "print('hello')"

        respx_mock.post("https://paste.pythondiscord.com/api/v1/paste").mock(return_value=httpx.Response(200, json={}))

        result = await paste(code)

        assert result == "Failed to upload formatted code."

    @pytest.mark.asyncio
    async def test_paste_request_format(self, respx_mock) -> None:
        """Test paste request includes correct format."""
        code = "print('hello')"
        paste_link = "https://paste.pythondiscord.com/abc123"

        route = respx_mock.post("https://paste.pythondiscord.com/api/v1/paste").mock(
            return_value=httpx.Response(200, json={"link": paste_link})
        )

        await paste(code)

        # Verify request payload
        assert route.called
        request = route.calls.last.request
        payload = json.loads(request.content)
        assert payload["expiry"] == "1day"
        assert len(payload["files"]) == 1
        assert payload["files"][0]["name"] == "byte-bot_formatted_code.py"
        assert payload["files"][0]["lexer"] == "python"
        assert payload["files"][0]["content"] == code

    @pytest.mark.asyncio
    async def test_paste_network_error(self, respx_mock) -> None:
        """Test paste with network error."""
        code = "print('hello')"

        respx_mock.post("https://paste.pythondiscord.com/api/v1/paste").mock(
            side_effect=httpx.ConnectError("Connection failed")
        )

        with pytest.raises(httpx.ConnectError):
            await paste(code)

    @pytest.mark.asyncio
    async def test_paste_empty_code(self, respx_mock) -> None:
        """Test paste with empty code string."""
        code = ""
        paste_link = "https://paste.pythondiscord.com/abc123"

        respx_mock.post("https://paste.pythondiscord.com/api/v1/paste").mock(
            return_value=httpx.Response(200, json={"link": paste_link})
        )

        result = await paste(code)

        assert result == paste_link

    @pytest.mark.asyncio
    async def test_paste_large_code(self, respx_mock) -> None:
        """Test paste with large code block."""
        code = "x = 1\n" * 1000  # 1000 lines
        paste_link = "https://paste.pythondiscord.com/abc123"

        respx_mock.post("https://paste.pythondiscord.com/api/v1/paste").mock(
            return_value=httpx.Response(200, json={"link": paste_link})
        )

        result = await paste(code)

        assert result == paste_link

    @pytest.mark.asyncio
    async def test_paste_null_link(self, respx_mock) -> None:
        """Test paste with explicit null link in response."""
        code = "print('hello')"

        respx_mock.post("https://paste.pythondiscord.com/api/v1/paste").mock(
            return_value=httpx.Response(200, json={"link": None})
        )

        result = await paste(code)

        assert result == "Failed to upload formatted code."


class TestChunkSequence:
    """Tests for chunk_sequence function."""

    def test_chunk_sequence_even_division(self) -> None:
        """Test chunking with even division."""
        sequence = [1, 2, 3, 4, 5, 6]
        result = list(chunk_sequence(sequence, 2))

        assert result == [(1, 2), (3, 4), (5, 6)]

    def test_chunk_sequence_uneven_division(self) -> None:
        """Test chunking with uneven division."""
        sequence = [1, 2, 3, 4, 5]
        result = list(chunk_sequence(sequence, 2))

        assert result == [(1, 2), (3, 4), (5,)]

    def test_chunk_sequence_single_chunk(self) -> None:
        """Test chunking that fits in single chunk."""
        sequence = [1, 2, 3]
        result = list(chunk_sequence(sequence, 5))

        assert result == [(1, 2, 3)]

    def test_chunk_sequence_empty(self) -> None:
        """Test chunking empty sequence."""
        sequence = []
        result = list(chunk_sequence(sequence, 2))

        assert result == []

    def test_chunk_sequence_size_one(self) -> None:
        """Test chunking with size one."""
        sequence = [1, 2, 3]
        result = list(chunk_sequence(sequence, 1))

        assert result == [(1,), (2,), (3,)]

    def test_chunk_sequence_with_strings(self) -> None:
        """Test chunking with string sequence."""
        sequence = ["a", "b", "c", "d", "e"]
        result = list(chunk_sequence(sequence, 2))

        assert result == [("a", "b"), ("c", "d"), ("e",)]

    def test_chunk_sequence_with_generator(self) -> None:
        """Test chunking with generator input."""
        sequence = (x for x in range(5))
        result = list(chunk_sequence(sequence, 2))

        assert result == [(0, 1), (2, 3), (4,)]

    def test_chunk_sequence_large_chunk_size(self) -> None:
        """Test chunking with chunk size larger than sequence."""
        sequence = [1, 2, 3]
        result = list(chunk_sequence(sequence, 100))

        assert result == [(1, 2, 3)]

    def test_chunk_sequence_with_mixed_types(self) -> None:
        """Test chunking with mixed type sequence."""
        sequence = [1, "a", 2.5, None, True]
        result = list(chunk_sequence(sequence, 2))

        assert result == [(1, "a"), (2.5, None), (True,)]

    def test_chunk_sequence_with_tuple_elements(self) -> None:
        """Test chunking sequence of tuples."""
        sequence = [(1, 2), (3, 4), (5, 6), (7, 8)]
        result = list(chunk_sequence(sequence, 2))

        assert result == [((1, 2), (3, 4)), ((5, 6), (7, 8))]

    def test_chunk_sequence_preserves_order(self) -> None:
        """Test that chunking preserves element order."""
        sequence = list(range(10))
        result = list(chunk_sequence(sequence, 3))

        flattened = [item for chunk in result for item in chunk]
        assert flattened == list(range(10))


class TestFormatResolutionLink:
    """Tests for format_resolution_link function."""

    def test_format_resolution_link_discussion_forum(self) -> None:
        """Test formatting discussion forum link."""
        resolution = "https://discuss.python.org/t/some-topic/12345"
        result = format_resolution_link(resolution)

        assert result == "[via Discussion Forum](https://discuss.python.org/t/some-topic/12345)"

    def test_format_resolution_link_mailing_list(self) -> None:
        """Test formatting mailing list link."""
        resolution = "https://mail.python.org/pipermail/some-list/2023-January/012345.html"
        result = format_resolution_link(resolution)

        assert result == "[via Mailist](https://mail.python.org/pipermail/some-list/2023-January/012345.html)"

    def test_format_resolution_link_none(self) -> None:
        """Test formatting None resolution."""
        result = format_resolution_link(None)

        assert result == "N/A"

    def test_format_resolution_link_other(self) -> None:
        """Test formatting other resolution types."""
        resolution = "https://github.com/python/peps/pull/1234"
        result = format_resolution_link(resolution)

        assert result == "https://github.com/python/peps/pull/1234"

    def test_format_resolution_link_empty_string(self) -> None:
        """Test formatting empty string resolution."""
        result = format_resolution_link("")

        assert result == "N/A"


class TestQueryAllPeps:
    """Tests for query_all_peps function."""

    @pytest.mark.asyncio
    async def test_query_all_peps_success(self, respx_mock) -> None:
        """Test successful PEP query."""
        mock_peps = {
            "8": {
                "number": 8,
                "title": "Style Guide for Python Code",
                "authors": "Guido van Rossum, Barry Warsaw",
                "discussions_to": "",
                "status": "Active",
                "type": "Process",
                "topic": "",
                "created": "05-Jul-2001",
                "python_version": None,
                "post_history": [],
                "resolution": None,
                "requires": None,
                "replaces": None,
                "superseded_by": None,
                "url": "https://peps.python.org/pep-0008/",
            }
        }

        respx_mock.get("https://peps.python.org/api/peps.json").mock(return_value=httpx.Response(200, json=mock_peps))

        peps = await query_all_peps()

        assert len(peps) == 1
        assert peps[0]["number"] == 8
        assert peps[0]["title"] == "Style Guide for Python Code"
        assert peps[0]["authors"] == ["Guido van Rossum", "Barry Warsaw"]
        assert peps[0]["status"] == PEPStatus.A
        assert peps[0]["type"] == PEPType.P
        assert peps[0]["created"] == "2001-07-05"
        assert peps[0]["resolution"] == "N/A"

    @pytest.mark.asyncio
    async def test_query_all_peps_with_resolution(self, respx_mock) -> None:
        """Test PEP query with resolution link."""
        mock_peps = {
            "484": {
                "number": 484,
                "title": "Type Hints",
                "authors": "Guido van Rossum",
                "discussions_to": "",
                "status": "Final",
                "type": "Standards Track",
                "topic": "",
                "created": "29-Sep-2014",
                "python_version": 3.5,
                "post_history": [],
                "resolution": "https://discuss.python.org/t/pep-484/12345",
                "requires": None,
                "replaces": None,
                "superseded_by": None,
                "url": "https://peps.python.org/pep-0484/",
            }
        }

        respx_mock.get("https://peps.python.org/api/peps.json").mock(return_value=httpx.Response(200, json=mock_peps))

        peps = await query_all_peps()

        assert len(peps) == 1
        assert "[via Discussion Forum]" in peps[0]["resolution"]

    @pytest.mark.asyncio
    async def test_query_all_peps_http_error(self, respx_mock) -> None:
        """Test PEP query with HTTP error."""
        respx_mock.get("https://peps.python.org/api/peps.json").mock(
            return_value=httpx.Response(500, json={"error": "Server error"})
        )

        with pytest.raises(httpx.HTTPStatusError):
            await query_all_peps()

    @pytest.mark.asyncio
    async def test_query_all_peps_multiple_peps(self, respx_mock) -> None:
        """Test query with multiple PEPs."""
        mock_peps = {
            "1": {
                "number": 1,
                "title": "PEP Purpose and Guidelines",
                "authors": "Barry Warsaw",
                "discussions_to": "",
                "status": "Active",
                "type": "Process",
                "topic": "",
                "created": "13-Jun-2000",
                "python_version": None,
                "post_history": [],
                "resolution": None,
                "requires": None,
                "replaces": None,
                "superseded_by": None,
                "url": "https://peps.python.org/pep-0001/",
            },
            "8": {
                "number": 8,
                "title": "Style Guide",
                "authors": "Guido van Rossum",
                "discussions_to": "",
                "status": "Active",
                "type": "Process",
                "topic": "",
                "created": "05-Jul-2001",
                "python_version": None,
                "post_history": [],
                "resolution": None,
                "requires": None,
                "replaces": None,
                "superseded_by": None,
                "url": "https://peps.python.org/pep-0008/",
            },
        }

        respx_mock.get("https://peps.python.org/api/peps.json").mock(return_value=httpx.Response(200, json=mock_peps))

        peps = await query_all_peps()

        assert len(peps) == 2
        numbers = [pep["number"] for pep in peps]
        assert 1 in numbers
        assert 8 in numbers

    @pytest.mark.asyncio
    async def test_query_all_peps_with_mailist_resolution(self, respx_mock) -> None:
        """Test PEP query with mailing list resolution link."""
        mock_peps = {
            "3100": {
                "number": 3100,
                "title": "Miscellaneous Python 3.0 Plans",
                "authors": "Brett Cannon",
                "discussions_to": "",
                "status": "Final",
                "type": "Process",
                "topic": "",
                "created": "01-Aug-2006",
                "python_version": None,
                "post_history": [],
                "resolution": "https://mail.python.org/pipermail/python-dev/2008-August/081822.html",
                "requires": None,
                "replaces": None,
                "superseded_by": None,
                "url": "https://peps.python.org/pep-3100/",
            }
        }

        respx_mock.get("https://peps.python.org/api/peps.json").mock(return_value=httpx.Response(200, json=mock_peps))

        peps = await query_all_peps()

        assert len(peps) == 1
        assert "[via Mailist]" in peps[0]["resolution"]

    @pytest.mark.asyncio
    async def test_query_all_peps_empty_response(self, respx_mock) -> None:
        """Test PEP query with empty response."""
        respx_mock.get("https://peps.python.org/api/peps.json").mock(return_value=httpx.Response(200, json={}))

        peps = await query_all_peps()

        assert len(peps) == 0

    @pytest.mark.asyncio
    async def test_query_all_peps_network_timeout(self, respx_mock) -> None:
        """Test PEP query with network timeout."""
        respx_mock.get("https://peps.python.org/api/peps.json").mock(
            side_effect=httpx.TimeoutException("Request timed out")
        )

        with pytest.raises(httpx.TimeoutException):
            await query_all_peps()

    @pytest.mark.asyncio
    async def test_query_all_peps_with_all_optional_fields(self, respx_mock) -> None:
        """Test PEP query with all optional fields populated."""
        mock_peps = {
            "570": {
                "number": 570,
                "title": "Python Positional-Only Parameters",
                "authors": "Larry Hastings, Pablo Galindo",
                "discussions_to": "https://discuss.python.org/t/pep-570/1078",
                "status": "Final",
                "type": "Standards Track",
                "topic": "typing",
                "created": "21-Jan-2018",
                "python_version": "3.8",
                "post_history": ["21-Jan-2018", "01-Feb-2018"],
                "resolution": "https://discuss.python.org/t/pep-570/1078",
                "requires": "484",
                "replaces": "3102",
                "superseded_by": "689",
                "url": "https://peps.python.org/pep-0570/",
            }
        }

        respx_mock.get("https://peps.python.org/api/peps.json").mock(return_value=httpx.Response(200, json=mock_peps))

        peps = await query_all_peps()

        assert len(peps) == 1
        pep = peps[0]
        assert pep["topic"] == "typing"
        assert pep["python_version"] == "3.8"
        assert pep["post_history"] == ["21-Jan-2018", "01-Feb-2018"]
        assert pep["requires"] == "484"
        assert pep["replaces"] == "3102"
        assert pep["superseded_by"] == "689"


class TestGetNextFriday:
    """Tests for get_next_friday function."""

    def test_get_next_friday_from_monday(self) -> None:
        """Test calculating next Friday from Monday."""
        # Monday 2025-11-17
        now = datetime(2025, 11, 17, 10, 30, tzinfo=UTC)
        start_dt, end_dt = get_next_friday(now)

        assert start_dt.weekday() == 4  # Friday
        assert start_dt.hour == 11
        assert start_dt.minute == 0
        assert end_dt == start_dt + __import__("datetime").timedelta(hours=1)

    def test_get_next_friday_from_friday_before_time(self) -> None:
        """Test calculating next Friday from Friday (before 11:00)."""
        # Friday 2025-11-21 at 09:00
        now = datetime(2025, 11, 21, 9, 0, tzinfo=UTC)
        start_dt, _ = get_next_friday(now)

        # Should be same day
        assert start_dt.day == 21
        assert start_dt.weekday() == 4  # Friday
        assert start_dt.hour == 11

    def test_get_next_friday_from_saturday(self) -> None:
        """Test calculating next Friday from Saturday."""
        # Saturday 2025-11-22
        now = datetime(2025, 11, 22, 10, 30, tzinfo=UTC)
        start_dt, _ = get_next_friday(now)

        # Should be next Friday (2025-11-28)
        assert start_dt.day == 28
        assert start_dt.weekday() == 4  # Friday

    def test_get_next_friday_with_delay(self) -> None:
        """Test calculating Friday with delay."""
        # Monday 2025-11-17
        now = datetime(2025, 11, 17, 10, 30, tzinfo=UTC)
        start_dt, _ = get_next_friday(now, delay=1)

        # Should be Friday + 1 week = 2025-11-28
        assert start_dt.day == 28
        assert start_dt.weekday() == 4  # Friday

    def test_get_next_friday_with_multiple_week_delay(self) -> None:
        """Test calculating Friday with multiple week delay."""
        # Monday 2025-11-17
        now = datetime(2025, 11, 17, 10, 30, tzinfo=UTC)
        start_dt, _ = get_next_friday(now, delay=2)

        # Should be Friday + 2 weeks = 2025-12-05
        assert start_dt.month == 12
        assert start_dt.day == 5
        assert start_dt.weekday() == 4  # Friday

    def test_get_next_friday_time_range(self) -> None:
        """Test that start and end times are one hour apart."""
        now = datetime(2025, 11, 17, 10, 30, tzinfo=UTC)
        start_dt, end_dt = get_next_friday(now)

        time_diff = end_dt - start_dt
        assert time_diff.total_seconds() == 3600  # 1 hour

    def test_get_next_friday_resets_time(self) -> None:
        """Test that time is reset to 11:00:00."""
        now = datetime(2025, 11, 17, 23, 59, 59, 999999, tzinfo=UTC)
        start_dt, _ = get_next_friday(now)

        assert start_dt.hour == 11
        assert start_dt.minute == 0
        assert start_dt.second == 0
        assert start_dt.microsecond == 0

    def test_get_next_friday_from_friday_after_time(self) -> None:
        """Test calculating next Friday from Friday (after 11:00)."""
        # Friday 2025-11-21 at 15:00
        # Note: function calculates next Friday from current day, not time
        now = datetime(2025, 11, 21, 15, 0, tzinfo=UTC)
        start_dt, _ = get_next_friday(now)

        # Should be same Friday (2025-11-21) - time doesn't affect the day calculation
        assert start_dt.day == 21
        assert start_dt.weekday() == 4  # Friday
        assert start_dt.hour == 11  # But time is reset to 11:00

    def test_get_next_friday_from_thursday(self) -> None:
        """Test calculating next Friday from Thursday."""
        # Thursday 2025-11-20
        now = datetime(2025, 11, 20, 10, 30, tzinfo=UTC)
        start_dt, _ = get_next_friday(now)

        # Should be next day (Friday 2025-11-21)
        assert start_dt.day == 21
        assert start_dt.weekday() == 4  # Friday

    def test_get_next_friday_preserves_timezone(self) -> None:
        """Test that timezone is preserved in result."""
        now = datetime(2025, 11, 17, 10, 30, tzinfo=UTC)
        start_dt, end_dt = get_next_friday(now)

        assert start_dt.tzinfo == UTC
        assert end_dt.tzinfo == UTC

    def test_get_next_friday_with_zero_delay(self) -> None:
        """Test calculating Friday with explicit zero delay."""
        # Monday 2025-11-17
        now = datetime(2025, 11, 17, 10, 30, tzinfo=UTC)
        start_dt_no_delay, _ = get_next_friday(now)
        start_dt_zero_delay, _ = get_next_friday(now, delay=0)

        # Should be same Friday
        assert start_dt_no_delay.day == start_dt_zero_delay.day


class TestSmartChunkText:
    """Tests for smart_chunk_text function."""

    def test_empty_text(self) -> None:
        """Test with empty text."""
        result = smart_chunk_text("")
        assert result == []

    def test_invalid_max_size_raises_error(self) -> None:
        """Test that non-positive max_size raises ValueError."""
        import pytest

        with pytest.raises(ValueError, match="max_size must be positive"):
            smart_chunk_text("test", max_size=0)

        with pytest.raises(ValueError, match="max_size must be positive"):
            smart_chunk_text("test", max_size=-1)

    def test_text_within_limit(self) -> None:
        """Test text that fits within max_size."""
        text = "Short text"
        result = smart_chunk_text(text, 100)
        assert result == ["Short text"]

    def test_splits_at_paragraph_boundary(self) -> None:
        """Test that splitting prefers paragraph boundaries."""
        text = "First paragraph.\n\nSecond paragraph."
        result = smart_chunk_text(text, 25)
        assert len(result) == 2
        assert result[0] == "First paragraph."
        assert result[1] == "Second paragraph."

    def test_splits_at_sentence_boundary(self) -> None:
        """Test that splitting falls back to sentence boundaries."""
        text = "First sentence. Second sentence. Third sentence."
        result = smart_chunk_text(text, 35)
        assert len(result) >= 2
        assert all(len(chunk) <= 35 for chunk in result)
        assert "First sentence." in result[0]

    def test_splits_at_newline(self) -> None:
        """Test that splitting falls back to newlines."""
        text = "Line one\nLine two\nLine three"
        result = smart_chunk_text(text, 15)
        assert len(result) >= 2
        assert all(len(chunk) <= 15 for chunk in result)

    def test_splits_at_word_boundary(self) -> None:
        """Test that splitting falls back to word boundaries."""
        text = "word1 word2 word3 word4 word5"
        result = smart_chunk_text(text, 12)
        assert len(result) >= 2
        assert all(len(chunk) <= 12 for chunk in result)

    def test_preserves_markdown_links(self) -> None:
        """Test that markdown links are not broken when they fit within max_size."""
        text = (
            "First paragraph with some text here.\n\n"
            "Check [this link](https://example.com/path) for more info.\n\n"
            "Third paragraph with more content."
        )
        result = smart_chunk_text(text, 80)
        for chunk in result:
            if "[this link]" in chunk:
                assert "[this link](https://example.com/path)" in chunk
                break
        else:
            combined = " ".join(result)
            assert "[this link](https://example.com/path)" in combined

    def test_preserves_inline_code(self) -> None:
        """Test that inline code is not broken when it fits within max_size."""
        text = "First sentence here.\n\nUse the `my_function()` method here.\n\nMore text follows."
        result = smart_chunk_text(text, 50)
        for chunk in result:
            if "`my_function()`" in chunk:
                break
        else:
            combined = " ".join(result)
            assert "`my_function()`" in combined

    def test_preserves_code_blocks(self) -> None:
        """Test that code blocks stay in the same chunk when they fit within max_size."""
        text = "Example:\n\n```python\ndef foo():\n    pass\n```\n\nEnd of content."
        result = smart_chunk_text(text, 60)

        block_chunk_found = False
        for chunk in result:
            backtick_fence_count = chunk.count("```")
            assert backtick_fence_count in (0, 2), "Chunk should not contain unmatched code fence"

            if "```python" in chunk:
                assert "def foo():" in chunk, "Code block content should stay with opening fence"
                assert chunk.count("```") == 2, "Opening and closing fences should be in same chunk"
                block_chunk_found = True

        assert block_chunk_found, "Should find a chunk containing the code block"

    def test_chunks_do_not_exceed_max_size(self) -> None:
        """Test that all chunks respect max_size limit."""
        text = "A" * 500 + " " + "B" * 500 + " " + "C" * 500
        result = smart_chunk_text(text, 600)
        for chunk in result:
            assert len(chunk) <= 600

    def test_multiple_markdown_links(self) -> None:
        """Test with multiple markdown links."""
        text = (
            "See [link1](https://example.com/1) and [link2](https://example.com/2) "
            "for more details on [link3](https://example.com/3)."
        )
        result = smart_chunk_text(text, 60)
        combined = " ".join(result)
        assert "[link1](https://example.com/1)" in combined
        assert "[link2](https://example.com/2)" in combined
        assert "[link3](https://example.com/3)" in combined

    def test_mixed_protected_regions(self) -> None:
        """Test with mixed markdown links and code."""
        text = "Use `code` and check [docs](https://docs.example.com) for help."
        result = smart_chunk_text(text, 40)
        combined = " ".join(result)
        assert "`code`" in combined
        assert "[docs](https://docs.example.com)" in combined

    def test_long_code_block_preserved(self) -> None:
        """Test that long code blocks spanning multiple lines are preserved."""
        code_block = "```\nline1\nline2\nline3\nline4\n```"
        text = f"Before\n\n{code_block}\n\nAfter"
        result = smart_chunk_text(text, 50)
        combined = "".join(result)
        assert code_block in combined

    def test_default_max_size(self) -> None:
        """Test that default max_size is 1000."""
        text = "A" * 1500
        result = smart_chunk_text(text)
        assert len(result) >= 2
        assert len(result[0]) <= 1000

    def test_real_world_ruff_explanation(self) -> None:
        """Test with content similar to ruff rule explanations."""
        text = (
            "**Why is this bad?**\n\n"
            "Long lines make code hard to read. See [PEP 8](https://pep8.org) for guidelines.\n\n"
            "**Example**\n\n"
            "```python\n"
            "x = 'very long string'\n"
            "```\n\n"
            "**Fix**\n\n"
            "Break the line using parentheses."
        )
        result = smart_chunk_text(text, 100)
        combined = "".join(result)
        assert "[PEP 8](https://pep8.org)" in combined
        assert "```python" in combined
        assert "```" in combined
