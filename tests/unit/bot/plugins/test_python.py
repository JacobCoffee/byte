"""Tests for python plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest

from byte_bot.plugins.python import Python, setup

if TYPE_CHECKING:
    from discord import Interaction
    from discord.ext.commands import Bot


@pytest.fixture
def mock_peps() -> list[dict]:
    """Mock PEP data."""
    return [
        {"number": 8, "title": "Style Guide for Python Code", "status": "Active", "type": "Process"},
        {"number": 20, "title": "The Zen of Python", "status": "Active", "type": "Informational"},
        {"number": 484, "title": "Type Hints", "status": "Final", "type": "Standards Track"},
    ]


class TestPythonCog:
    """Tests for Python cog."""

    def test_python_cog_initialization(self, mock_bot: Bot, mock_peps: list[dict]) -> None:
        """Test Python cog initializes correctly."""
        cog = Python(mock_bot, mock_peps)

        assert cog.bot == mock_bot
        assert cog.__cog_name__ == "Python Commands"
        assert len(cog._peps) == 3
        assert 8 in cog._peps
        assert 20 in cog._peps
        assert 484 in cog._peps

    @pytest.mark.asyncio
    async def test_pep_autocomplete(self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]) -> None:
        """Test _pep_autocomplete returns choices."""
        cog = Python(mock_bot, mock_peps)

        choices = await cog._pep_autocomplete(mock_interaction, "Style")

        assert len(choices) > 0
        assert any("PEP 8" in choice.name for choice in choices)

    @pytest.mark.asyncio
    async def test_pep_autocomplete_by_number(self, mock_bot: Bot, mock_interaction: Interaction, mock_peps: list[dict]) -> None:
        """Test _pep_autocomplete filters by number."""
        cog = Python(mock_bot, mock_peps)

        choices = await cog._pep_autocomplete(mock_interaction, "484")

        assert len(choices) == 1
        assert "PEP 484" in choices[0].name

    @pytest.mark.asyncio
    async def test_pep_autocomplete_limits_to_25(self, mock_bot: Bot, mock_interaction: Interaction) -> None:
        """Test _pep_autocomplete limits to 25 choices."""
        # Create 30 PEPs
        many_peps = [{"number": i, "title": f"PEP {i}"} for i in range(30)]
        cog = Python(mock_bot, many_peps)

        choices = await cog._pep_autocomplete(mock_interaction, "")

        assert len(choices) <= 25

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
