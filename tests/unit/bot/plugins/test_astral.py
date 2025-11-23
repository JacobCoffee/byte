"""Tests for astral plugin commands."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from byte_bot.plugins.astral import Astral, setup

if TYPE_CHECKING:
    from discord import Interaction
    from discord.ext.commands import Bot


@pytest.fixture
def mock_ruff_rules() -> list[dict]:
    """Mock Ruff rule data."""
    return [
        {
            "code": "F401",
            "name": "unused-import",
            "summary": "Module imported but unused",
            "explanation": "## Example\nImports should be used.",
            "fix": "Remove the unused import.",
        },
        {
            "code": "E501",
            "name": "line-too-long",
            "summary": "Line too long",
            "explanation": "## Line Length\nLines should be under 88 characters.",
            "fix": "Break the line.",
        },
        {
            "code": "W605",
            "name": "invalid-escape-sequence",
            "summary": "Invalid escape sequence",
            "explanation": "## Escape Sequences\nUse raw strings for regex.",
            "fix": "Use r-strings.",
        },
    ]


class TestAstralCog:
    """Tests for Astral cog."""

    def test_astral_cog_initialization(self, mock_bot: Bot, mock_ruff_rules: list[dict]) -> None:
        """Test Astral cog initializes correctly."""
        cog = Astral(mock_bot, mock_ruff_rules)

        assert cog.bot == mock_bot
        assert cog.__cog_name__ == "Astral Commands"
        assert len(cog._rules) == 3
        assert "F401" in cog._rules
        assert "E501" in cog._rules
        assert "W605" in cog._rules

    @pytest.mark.asyncio
    async def test_rule_autocomplete_by_code(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test _rule_autocomplete filters by rule code."""
        cog = Astral(mock_bot, mock_ruff_rules)

        choices = await cog._rule_autocomplete(mock_interaction, "F401")

        assert len(choices) == 1
        assert "F401" in choices[0].name
        assert "unused-import" in choices[0].name
        assert choices[0].value == "F401"

    @pytest.mark.asyncio
    async def test_rule_autocomplete_by_name(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test _rule_autocomplete filters by rule code substring."""
        cog = Astral(mock_bot, mock_ruff_rules)

        # The autocomplete searches in code, not name
        choices = await cog._rule_autocomplete(mock_interaction, "E50")

        assert len(choices) == 1
        assert "E501" in choices[0].name
        assert "line-too-long" in choices[0].name

    @pytest.mark.asyncio
    async def test_rule_autocomplete_case_insensitive(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test _rule_autocomplete is case insensitive."""
        cog = Astral(mock_bot, mock_ruff_rules)

        # Search by rule code (case insensitive)
        choices = await cog._rule_autocomplete(mock_interaction, "w60")

        assert len(choices) == 1
        assert "W605" in choices[0].name

    @pytest.mark.asyncio
    async def test_rule_autocomplete_limits_to_25(self, mock_bot: Bot, mock_interaction: Interaction) -> None:
        """Test _rule_autocomplete limits to 25 choices."""
        # Create 30 rules
        many_rules = [{"code": f"E{i:03d}", "name": f"rule-{i}"} for i in range(30)]
        cog = Astral(mock_bot, many_rules)

        choices = await cog._rule_autocomplete(mock_interaction, "E")

        assert len(choices) == 25

    @pytest.mark.asyncio
    async def test_rule_autocomplete_empty_query(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test _rule_autocomplete with empty query returns all rules (up to 25)."""
        cog = Astral(mock_bot, mock_ruff_rules)

        choices = await cog._rule_autocomplete(mock_interaction, "")

        assert len(choices) == 3

    @pytest.mark.asyncio
    async def test_ruff_rule_command_success(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test /ruff command with valid rule."""
        cog = Astral(mock_bot, mock_ruff_rules)

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345

        # Call the command
        await cog.ruff_rule.callback(cog, mock_interaction, "F401")

        # Should send processing message
        mock_interaction.response.send_message.assert_called_once_with("Querying Ruff rule...", ephemeral=True)

        # Should send embed with rule details
        mock_interaction.followup.send.assert_called_once()
        call_kwargs = mock_interaction.followup.send.call_args[1]

        # Check embed
        embed = call_kwargs["embed"]
        assert "unused-import" in embed.title
        assert embed.color.value == 0xD7FF64  # astral_yellow

        # Check view
        assert "view" in call_kwargs

    @pytest.mark.asyncio
    async def test_ruff_rule_command_not_found(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test /ruff command with invalid rule."""
        cog = Astral(mock_bot, mock_ruff_rules)

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        # Call the command with invalid rule
        await cog.ruff_rule.callback(cog, mock_interaction, "INVALID")

        # Should send processing message
        mock_interaction.response.send_message.assert_called_once()

        # Should send error embed
        mock_interaction.followup.send.assert_called_once()
        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        assert "not found" in embed.title

    @pytest.mark.asyncio
    async def test_ruff_rule_embed_fields(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test /ruff command creates embed with all required fields."""
        cog = Astral(mock_bot, mock_ruff_rules)

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345

        # Call the command
        await cog.ruff_rule.callback(cog, mock_interaction, "E501")

        # Check embed fields
        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        embed_dict = embed.to_dict()

        # Should have summary and documentation fields (minified)
        field_names = [field["name"] for field in embed_dict.get("fields", [])]
        assert "Summary" in field_names
        assert "Documentation" in field_names

    @pytest.mark.asyncio
    async def test_format_code_command_not_implemented(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test /format command returns not ready message."""
        cog = Astral(mock_bot, mock_ruff_rules)

        mock_interaction.response.send_message = AsyncMock()

        # Call the command
        await cog.format_code.callback(cog, mock_interaction, "print('test')")

        # Should send not ready message
        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args[0][0]
        assert "not yet ready" in call_args

    @pytest.mark.asyncio
    async def test_ruff_rule_with_long_explanation(self, mock_bot: Bot, mock_interaction: Interaction) -> None:
        """Test /ruff command chunks long explanations."""
        long_rule = {
            "code": "LONG1",
            "name": "long-rule",
            "summary": "A rule with a long explanation",
            "explanation": "x" * 3000,  # Long explanation that needs chunking
            "fix": "Fix it",
        }
        cog = Astral(mock_bot, [long_rule])

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345

        # Call the command
        await cog.ruff_rule.callback(cog, mock_interaction, "LONG1")

        # Should still succeed
        mock_interaction.followup.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_setup_adds_cog_to_bot(self, mock_bot: Bot) -> None:
        """Test setup function adds Astral cog to bot."""
        mock_bot.add_cog = AsyncMock()

        # Mock query_all_ruff_rules
        with patch("byte_bot.plugins.astral.query_all_ruff_rules", return_value=[]):
            await setup(mock_bot)

            mock_bot.add_cog.assert_called_once()
            cog = mock_bot.add_cog.call_args[0][0]
            assert isinstance(cog, Astral)
            assert cog.bot == mock_bot

    @pytest.mark.asyncio
    async def test_setup_queries_ruff_rules(self, mock_bot: Bot, mock_ruff_rules: list[dict]) -> None:
        """Test setup function queries Ruff rules."""
        mock_bot.add_cog = AsyncMock()

        with patch("byte_bot.plugins.astral.query_all_ruff_rules", return_value=mock_ruff_rules) as mock_query:
            await setup(mock_bot)

            # Should have called query function
            mock_query.assert_called_once()

            # Cog should have rules
            cog = mock_bot.add_cog.call_args[0][0]
            assert len(cog._rules) == 3

    @pytest.mark.asyncio
    async def test_rule_autocomplete_no_matches(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test _rule_autocomplete returns empty when no matches."""
        cog = Astral(mock_bot, mock_ruff_rules)

        choices = await cog._rule_autocomplete(mock_interaction, "ZZZZZ")

        assert len(choices) == 0

    @pytest.mark.asyncio
    async def test_rule_autocomplete_partial_match(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test _rule_autocomplete with partial code match."""
        cog = Astral(mock_bot, mock_ruff_rules)

        choices = await cog._rule_autocomplete(mock_interaction, "F4")

        assert len(choices) == 1
        assert "F401" in choices[0].name

    @pytest.mark.asyncio
    async def test_rule_autocomplete_choice_format(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test _rule_autocomplete formats choices correctly."""
        cog = Astral(mock_bot, mock_ruff_rules)

        choices = await cog._rule_autocomplete(mock_interaction, "F401")

        assert len(choices) == 1
        # Format: "CODE - name"
        assert " - " in choices[0].name
        assert choices[0].value == "F401"

    @pytest.mark.asyncio
    async def test_ruff_rule_embed_has_thumbnail(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test /ruff command embed includes Ruff logo thumbnail."""
        cog = Astral(mock_bot, mock_ruff_rules)

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345

        await cog.ruff_rule.callback(cog, mock_interaction, "F401")

        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        embed_dict = embed.to_dict()

        assert "thumbnail" in embed_dict
        assert "ruff" in embed_dict["thumbnail"]["url"].lower()

    @pytest.mark.asyncio
    async def test_ruff_rule_creates_both_embeds(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test /ruff command creates both minified and full embeds."""
        cog = Astral(mock_bot, mock_ruff_rules)

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345

        await cog.ruff_rule.callback(cog, mock_interaction, "F401")

        call_kwargs = mock_interaction.followup.send.call_args[1]
        view = call_kwargs["view"]

        # View should have both embeds
        assert hasattr(view, "original_embed")
        assert hasattr(view, "minified_embed")

    @pytest.mark.asyncio
    async def test_ruff_rule_documentation_links(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test /ruff command includes documentation links."""
        cog = Astral(mock_bot, mock_ruff_rules)

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        mock_interaction.user = MagicMock()
        mock_interaction.user.id = 12345

        await cog.ruff_rule.callback(cog, mock_interaction, "F401")

        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        embed_dict = embed.to_dict()

        # Find documentation field
        doc_field = next((f for f in embed_dict.get("fields", []) if f["name"] == "Documentation"), None)
        assert doc_field is not None
        assert "docs.astral.sh" in doc_field["value"]

    @pytest.mark.asyncio
    async def test_format_code_ephemeral(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test /format command sends ephemeral message."""
        cog = Astral(mock_bot, mock_ruff_rules)

        mock_interaction.response.send_message = AsyncMock()

        await cog.format_code.callback(cog, mock_interaction, "print('test')")

        mock_interaction.response.send_message.assert_called_once()
        call_kwargs = mock_interaction.response.send_message.call_args
        assert call_kwargs[1].get("ephemeral") is True

    @pytest.mark.asyncio
    async def test_ruff_rule_not_found_color(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_ruff_rules: list[dict]
    ) -> None:
        """Test /ruff command not found uses purple color."""
        cog = Astral(mock_bot, mock_ruff_rules)

        mock_interaction.response.send_message = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        await cog.ruff_rule.callback(cog, mock_interaction, "INVALID")

        call_kwargs = mock_interaction.followup.send.call_args[1]
        embed = call_kwargs["embed"]
        assert embed.color.value == 0x261230  # astral_purple

    @pytest.mark.asyncio
    async def test_rules_dictionary_lookup_performance(self, mock_bot: Bot, mock_ruff_rules: list[dict]) -> None:
        """Test rules are stored in dictionary for O(1) lookup."""
        cog = Astral(mock_bot, mock_ruff_rules)

        # Direct dictionary access should be instant
        assert "F401" in cog._rules
        assert cog._rules["F401"]["name"] == "unused-import"

    @pytest.mark.asyncio
    async def test_astral_cog_name(self, mock_bot: Bot, mock_ruff_rules: list[dict]) -> None:
        """Test Astral cog has correct display name."""
        cog = Astral(mock_bot, mock_ruff_rules)

        assert cog.__cog_name__ == "Astral Commands"
