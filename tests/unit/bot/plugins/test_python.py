"""Tests for python plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from byte_bot.plugins.python import Python, setup

if TYPE_CHECKING:
    from discord import Interaction
    from discord.ext.commands import Bot


@pytest.fixture
def mock_peps() -> list[dict]:
    """Mock PEP data."""
    return [
        {
            "number": 8,
            "title": "Style Guide for Python Code",
            "status": "Active",
            "type": "Process",
            "python_version": "N/A",
            "created": "2001-03-05",
            "authors": ["Guido van Rossum", "Barry Warsaw"],
            "url": "https://peps.python.org/pep-0008/",
            "resolution": "N/A",
        },
        {
            "number": 20,
            "title": "The Zen of Python",
            "status": "Active",
            "type": "Informational",
            "python_version": "N/A",
            "created": "2004-08-19",
            "authors": ["Tim Peters"],
            "url": "https://peps.python.org/pep-0020/",
            "resolution": "N/A",
        },
        {
            "number": 484,
            "title": "Type Hints",
            "status": "Final",
            "type": "Standards Track",
            "python_version": "3.5",
            "created": "2014-09-29",
            "authors": ["Guido van Rossum", "Jukka Lehtosalo", "Łukasz Langa"],
            "url": "https://peps.python.org/pep-0484/",
            "resolution": "https://discuss.python.org/t/484/123",
            "topic": "Typing",
            "requires": "N/A",
            "replaces": "N/A",
            "superseded_by": "N/A",
            "discussions_to": "python-dev@python.org",
            "post_history": "2014-09-29, 2014-10-01",
        },
        {
            "number": 572,
            "title": "Assignment Expressions",
            "status": "Final",
            "type": "Standards Track",
            "python_version": "3.8",
            "created": "2018-02-28",
            "authors": ["Chris Angelico"],
            "url": "https://peps.python.org/pep-0572/",
            "resolution": "N/A",
        },
    ]


class TestPythonCog:
    """Tests for Python cog."""

    def test_python_cog_initialization(self, mock_bot: Bot, mock_peps: list[dict]) -> None:
        """Test Python cog initializes correctly."""
        cog = Python(mock_bot, mock_peps)

        assert cog.bot == mock_bot
        assert cog.__cog_name__ == "Python Commands"
        assert len(cog._peps) == 4
        assert 8 in cog._peps
        assert 20 in cog._peps
        assert 484 in cog._peps
        assert 572 in cog._peps

    @pytest.mark.asyncio
    async def test_pep_autocomplete_by_title(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test _pep_autocomplete filters by title."""
        cog = Python(mock_bot, mock_peps)

        choices = await cog._pep_autocomplete(mock_interaction, "Style")

        assert len(choices) > 0
        assert any("PEP 8" in choice.name for choice in choices)
        assert any("Style Guide" in choice.name for choice in choices)

    @pytest.mark.asyncio
    async def test_pep_autocomplete_by_number(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test _pep_autocomplete filters by number."""
        cog = Python(mock_bot, mock_peps)

        choices = await cog._pep_autocomplete(mock_interaction, "484")

        assert len(choices) == 1
        assert "PEP 484" in choices[0].name
        assert "Type Hints" in choices[0].name
        assert choices[0].value == "484"

    @pytest.mark.asyncio
    async def test_pep_autocomplete_partial_number(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test _pep_autocomplete with partial number match."""
        cog = Python(mock_bot, mock_peps)

        choices = await cog._pep_autocomplete(mock_interaction, "8")

        # Should match PEP 8 and PEP 484 (contains '8')
        assert len(choices) >= 1
        assert any("PEP 8" in choice.name for choice in choices)

    @pytest.mark.asyncio
    async def test_pep_autocomplete_case_insensitive(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test _pep_autocomplete is case insensitive."""
        cog = Python(mock_bot, mock_peps)

        choices = await cog._pep_autocomplete(mock_interaction, "ZEN")

        assert len(choices) == 1
        assert "PEP 20" in choices[0].name
        assert "Zen of Python" in choices[0].name

    @pytest.mark.asyncio
    async def test_pep_autocomplete_limits_to_25(self, mock_bot: Bot, mock_interaction: Interaction) -> None:
        """Test _pep_autocomplete limits to 25 choices."""
        # Create 30 PEPs
        many_peps = [{"number": i, "title": f"Test PEP {i}"} for i in range(30)]
        cog = Python(mock_bot, many_peps)

        choices = await cog._pep_autocomplete(mock_interaction, "")

        assert len(choices) == 25

    @pytest.mark.asyncio
    async def test_pep_autocomplete_empty_query(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test _pep_autocomplete with empty query returns all PEPs (up to 25)."""
        cog = Python(mock_bot, mock_peps)

        choices = await cog._pep_autocomplete(mock_interaction, "")

        assert len(choices) == 4

    @pytest.mark.asyncio
    async def test_peps_command_success(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test /pep command with valid PEP number."""
        cog = Python(mock_bot, mock_peps)

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345

        # Call the command
        await cog.peps.callback(cog, mock_interaction, 8)

        # Should send processing message
        mock_interaction.response.send_message.assert_called_once_with("Querying PEP 8...", ephemeral=True)

        # Should send embed with PEP details
        mock_interaction.followup.send.assert_called_once()
        call_kwargs = mock_interaction.followup.send.call_args[1]

        # Check embed
        embed = call_kwargs["embed"]
        assert "PEP 8" in embed.title
        assert "Style Guide" in embed.title
        assert embed.color.value == 0x4B8BBE  # python_blue

        # Check view
        assert "view" in call_kwargs

    @pytest.mark.asyncio
    async def test_peps_command_not_found(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test /pep command with invalid PEP number."""
        cog = Python(mock_bot, mock_peps)

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        # Call the command with non-existent PEP
        await cog.peps.callback(cog, mock_interaction, 9999)

        # Should send processing message
        mock_interaction.response.send_message.assert_called_once()

        # Should send error embed
        mock_interaction.followup.send.assert_called_once()
        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        assert "not found" in embed.title
        assert call_kwargs.get("ephemeral") is True

    @pytest.mark.asyncio
    async def test_peps_command_embed_fields(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test /pep command creates embed with all required fields."""
        cog = Python(mock_bot, mock_peps)

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345

        # Call the command with PEP 484 (has all fields)
        await cog.peps.callback(cog, mock_interaction, 484)

        # Check embed fields
        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        embed_dict = embed.to_dict()

        # Should have required fields in minified view
        field_names = [field["name"] for field in embed_dict.get("fields", [])]
        assert "Status" in field_names
        assert "Python Version" in field_names
        assert "Created" in field_names
        assert "Resolution" in field_names
        assert "Documentation" in field_names

    @pytest.mark.asyncio
    async def test_peps_command_multiple_peps(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test /pep command with different PEP numbers."""
        cog = Python(mock_bot, mock_peps)

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345

        # Test PEP 20
        await cog.peps.callback(cog, mock_interaction, 20)
        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        assert "PEP 20" in embed.title
        assert "Zen of Python" in embed.title

        # Reset mocks
        mock_interaction.response.send_message.reset_mock()
        mock_interaction.followup.send.reset_mock()

        # Test PEP 572
        await cog.peps.callback(cog, mock_interaction, 572)
        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        assert "PEP 572" in embed.title
        assert "Assignment Expressions" in embed.title

    @pytest.mark.asyncio
    async def test_peps_command_with_optional_fields(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test /pep command handles optional fields correctly."""
        cog = Python(mock_bot, mock_peps)

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345

        # PEP 484 has all optional fields
        await cog.peps.callback(cog, mock_interaction, 484)
        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]

        # Should not crash and should display fields
        assert embed is not None

    @pytest.mark.asyncio
    async def test_setup_adds_cog_to_bot(self, mock_bot: Bot) -> None:
        """Test setup function adds Python cog to bot."""
        mock_bot.add_cog = AsyncMock()

        # Mock query_all_peps
        with patch("byte_bot.plugins.python.query_all_peps", return_value=[]):
            await setup(mock_bot)

            mock_bot.add_cog.assert_called_once()
            cog = mock_bot.add_cog.call_args[0][0]
            assert isinstance(cog, Python)
            assert cog.bot == mock_bot

    @pytest.mark.asyncio
    async def test_setup_queries_peps(self, mock_bot: Bot, mock_peps: list[dict]) -> None:
        """Test setup function queries PEPs from API."""
        mock_bot.add_cog = AsyncMock()

        with patch("byte_bot.plugins.python.query_all_peps", return_value=mock_peps) as mock_query:
            await setup(mock_bot)

            # Should have called query function
            mock_query.assert_called_once()

            # Cog should have PEPs
            cog = mock_bot.add_cog.call_args[0][0]
            assert len(cog._peps) == 4

    @pytest.mark.asyncio
    async def test_peps_command_url_in_embed(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test /pep command includes PEP URL in embed."""
        cog = Python(mock_bot, mock_peps)

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345

        # Call the command
        await cog.peps.callback(cog, mock_interaction, 8)

        # Check that URL is in embed
        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        embed_dict = embed.to_dict()

        # Find documentation field
        doc_field = next((f for f in embed_dict.get("fields", []) if f["name"] == "Documentation"), None)
        assert doc_field is not None
        assert "peps.python.org/pep-0008" in doc_field["value"]

    @pytest.mark.asyncio
    async def test_pep_autocomplete_no_matches(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test _pep_autocomplete returns empty when no matches."""
        cog = Python(mock_bot, mock_peps)
        choices = await cog._pep_autocomplete(mock_interaction, "ZZZZZ")
        assert len(choices) == 0

    @pytest.mark.asyncio
    async def test_pep_autocomplete_choice_format(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test _pep_autocomplete formats choices correctly."""
        cog = Python(mock_bot, mock_peps)
        choices = await cog._pep_autocomplete(mock_interaction, "8")
        assert len(choices) > 0
        assert "PEP" in choices[0].name
        assert " - " in choices[0].name
        assert choices[0].value.isdigit()

    @pytest.mark.asyncio
    async def test_peps_command_embed_thumbnail(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test /pep command embed includes Python logo thumbnail."""
        cog = Python(mock_bot, mock_peps)
        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345
        await cog.peps.callback(cog, mock_interaction, 8)
        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        embed_dict = embed.to_dict()
        assert "thumbnail" in embed_dict
        assert "python" in embed_dict["thumbnail"]["url"].lower()

    @pytest.mark.asyncio
    async def test_peps_command_creates_both_embeds(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test /pep command creates both minified and full embeds."""
        cog = Python(mock_bot, mock_peps)
        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345
        await cog.peps.callback(cog, mock_interaction, 484)
        call_kwargs = mock_interaction.followup.send.call_args[1]
        view = call_kwargs["view"]
        assert hasattr(view, "original_embed")
        assert hasattr(view, "minified_embed")

    @pytest.mark.asyncio
    async def test_peps_command_not_found_color(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test /pep command not found uses yellow color."""
        cog = Python(mock_bot, mock_peps)
        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        await cog.peps.callback(cog, mock_interaction, 9999)
        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        assert embed.color.value == 0xFFD43B

    @pytest.mark.asyncio
    async def test_peps_command_handles_missing_optional_fields(
        self, mock_bot: Bot, mock_interaction: Interaction
    ) -> None:
        """Test /pep command handles PEPs with missing optional fields."""
        minimal_pep = {
            "number": 999,
            "title": "Minimal PEP",
            "status": "Draft",
            "type": "Informational",
            "python_version": "N/A",
            "created": "2024-01-01",
            "authors": ["Test Author"],
            "url": "https://peps.python.org/pep-0999/",
            "resolution": "N/A",
        }
        cog = Python(mock_bot, [minimal_pep])
        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345
        await cog.peps.callback(cog, mock_interaction, 999)
        mock_interaction.followup.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_peps_dictionary_lookup_performance(self, mock_bot: Bot, mock_peps: list[dict]) -> None:
        """Test PEPs are stored in dictionary for O(1) lookup."""
        cog = Python(mock_bot, mock_peps)
        assert 8 in cog._peps
        assert cog._peps[8]["title"] == "Style Guide for Python Code"

    @pytest.mark.asyncio
    async def test_python_cog_name(self, mock_bot: Bot, mock_peps: list[dict]) -> None:
        """Test Python cog has correct display name."""
        cog = Python(mock_bot, mock_peps)
        assert cog.__cog_name__ == "Python Commands"

    @pytest.mark.asyncio
    async def test_pep_autocomplete_matches_both_title_and_number(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]
    ) -> None:
        """Test _pep_autocomplete searches both title and number."""
        cog = Python(mock_bot, mock_peps)
        choices_by_number = await cog._pep_autocomplete(mock_interaction, "484")
        assert len(choices_by_number) == 1
        choices_by_title = await cog._pep_autocomplete(mock_interaction, "Type Hints")
        assert len(choices_by_title) == 1
