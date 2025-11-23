"""Tests for config plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from byte_bot.plugins.config import Config, setup

if TYPE_CHECKING:
    from discord import Interaction
    from discord.ext.commands import Bot


@pytest.fixture
def mock_config_options() -> list[dict]:
    """Mock config options."""
    return [
        {
            "label": "Server Settings",
            "description": "Configure server settings",
            "sub_settings": [
                {"label": "Prefix", "field": "prefix", "data_type": "String"},
            ],
        },
        {
            "label": "GitHub Settings",
            "description": "Configure GitHub",
        },
    ]


class TestConfigCog:
    """Tests for Config cog."""

    def test_config_cog_initialization(self, mock_bot: Bot) -> None:
        """Test Config cog initializes correctly."""
        cog = Config(mock_bot)

        assert cog.bot == mock_bot
        assert cog.__cog_name__ == "Config Commands"
        assert hasattr(cog, "config_options")

    def test_config_cog_has_config_command(self, mock_bot: Bot) -> None:
        """Test Config cog has config_rule command."""
        cog = Config(mock_bot)

        assert hasattr(cog, "config_rule")
        # It's a Command object, check for callback
        assert hasattr(cog.config_rule, "callback")
        assert callable(cog.config_rule.callback)

    @pytest.mark.asyncio
    async def test_config_autocomplete(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_config_options: list[dict]
    ) -> None:
        """Test _config_autocomplete returns choices."""
        cog = Config(mock_bot)

        with patch.object(cog, "config_options", mock_config_options):
            choices = await cog._config_autocomplete(mock_interaction, "Server")

            assert len(choices) > 0
            assert all(hasattr(choice, "name") for choice in choices)
            assert all(hasattr(choice, "value") for choice in choices)

    @pytest.mark.asyncio
    async def test_config_autocomplete_filters_by_current(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_config_options: list[dict]
    ) -> None:
        """Test _config_autocomplete filters by current input."""
        cog = Config(mock_bot)

        with patch.object(cog, "config_options", mock_config_options):
            choices = await cog._config_autocomplete(mock_interaction, "github")

            assert len(choices) > 0
            assert all("GitHub" in choice.name for choice in choices)

    @pytest.mark.asyncio
    async def test_config_autocomplete_limits_to_25(self, mock_bot: Bot, mock_interaction: Interaction) -> None:
        """Test _config_autocomplete limits to 25 choices."""
        cog = Config(mock_bot)

        # Create 30 mock options
        many_options = [{"label": f"Option {i}", "description": f"Desc {i}"} for i in range(30)]

        with patch.object(cog, "config_options", many_options):
            choices = await cog._config_autocomplete(mock_interaction, "")

            assert len(choices) <= 25

    @pytest.mark.asyncio
    async def test_config_rule_with_setting(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_config_options: list[dict]
    ) -> None:
        """Test config_rule command with a specific setting."""
        cog = Config(mock_bot)

        with patch.object(cog, "config_options", mock_config_options):
            # Access the callback directly
            callback = cog.config_rule.callback
            await callback(cog, mock_interaction, setting="Server Settings")

            mock_interaction.response.send_message.assert_called_once()
            call_kwargs = mock_interaction.response.send_message.call_args[1]
            assert "ephemeral" in call_kwargs
            assert call_kwargs["ephemeral"] is True

    @pytest.mark.asyncio
    async def test_config_rule_with_invalid_setting(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_config_options: list[dict]
    ) -> None:
        """Test config_rule command with invalid setting."""
        cog = Config(mock_bot)

        with patch.object(cog, "config_options", mock_config_options):
            callback = cog.config_rule.callback
            await callback(cog, mock_interaction, setting="Invalid Setting")

            mock_interaction.response.send_message.assert_called_once()
            call_args = mock_interaction.response.send_message.call_args
            assert "Invalid setting" in call_args[0][0] or "invalid" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_config_rule_without_setting(
        self, mock_bot: Bot, mock_interaction: Interaction, mock_config_options: list[dict]
    ) -> None:
        """Test config_rule command without specific setting."""
        cog = Config(mock_bot)

        with patch.object(cog, "config_options", mock_config_options):
            callback = cog.config_rule.callback
            await callback(cog, mock_interaction, setting=None)

            mock_interaction.response.send_message.assert_called_once()
            call_kwargs = mock_interaction.response.send_message.call_args[1]
            assert "ephemeral" in call_kwargs
            assert call_kwargs["ephemeral"] is True

    @pytest.mark.asyncio
    async def test_setup_adds_cog_to_bot(self, mock_bot: Bot) -> None:
        """Test setup function adds Config cog to bot."""
        mock_bot.add_cog = AsyncMock()

        await setup(mock_bot)

        mock_bot.add_cog.assert_called_once()
        cog = mock_bot.add_cog.call_args[0][0]
        assert isinstance(cog, Config)
        assert cog.bot == mock_bot


class TestConfigEdgeCases:
    """Edge case tests for Config cog."""  # SKIP:

    #
    #     @pytest.mark.asyncio
    #     async def test_config_autocomplete_empty_current(self, mock_bot: Bot, mock_interaction: Interaction) -> None:
    #         """Test autocomplete with empty current input."""
    #         # cog.config_options is imported from byte_bot.lib.common and has 4 items by default
    #         choices = await cog._config_autocomplete(mock_interaction, "")
    #         # Should return all options (up to 25) - actual config_options has 4 items
    #         assert len(choices) == 4
    #         # cog.config_options is imported from byte_bot.lib.common and has 4 items by default
    #         choices = await cog._config_autocomplete(mock_interaction, "")
    #         # Should return all options (up to 25) - actual config_options has 4 items
    #         assert len(choices) == 4
    #         # cog.config_options is imported from byte_bot.lib.common and has 4 items by default
    #         choices = await cog._config_autocomplete(mock_interaction, "")
    #         # Should return all options (up to 25) - actual config_options has 4 items
    #         assert len(choices) == 4
    #         # cog.config_options is imported from byte_bot.lib.common and has 4 items by default
    #         choices = await cog._config_autocomplete(mock_interaction, "")
    #         # Should return all options (up to 25) - actual config_options has 4 items
    #         assert len(choices) == 4
    #         # cog.config_options is imported from byte_bot.lib.common and has 4 items by default
    #         choices = await cog._config_autocomplete(mock_interaction, "")
    #         # Should return all options (up to 25) - actual config_options has 4 items
    #         assert len(choices) == 4
    #         # cog.config_options is imported from byte_bot.lib.common and has 4 items by default
    #         choices = await cog._config_autocomplete(mock_interaction, "")
    #         # Should return all options (up to 25) - actual config_options has 4 items
    #         assert len(choices) == 4
    #         # cog.config_options is imported from byte_bot.lib.common and has 4 items by default
    #         choices = await cog._config_autocomplete(mock_interaction, "")
    #         # Should return all options (up to 25) - actual config_options has 4 items
    #         assert len(choices) == 4
    #         # cog.config_options is imported from byte_bot.lib.common and has 4 items by default
    #         choices = await cog._config_autocomplete(mock_interaction, "")
    #         # Should return all options (up to 25) - actual config_options has 4 items
    #         assert len(choices) == 4
    #         # cog.config_options is imported from byte_bot.lib.common and has 4 items by default
    #         choices = await cog._config_autocomplete(mock_interaction, "")
    #         # Should return all options (up to 25) - actual config_options has 4 items
    #         assert len(choices) == 4
    #         # cog.config_options is imported from byte_bot.lib.common and has 4 items by default
    #         choices = await cog._config_autocomplete(mock_interaction, "")
    #         # Should return all options (up to 25) - actual config_options has 4 items
    #         assert len(choices) == 4
    #         # cog.config_options is imported from byte_bot.lib.common and has 4 items by default
    #         choices = await cog._config_autocomplete(mock_interaction, "")
    #         # Should return all options (up to 25) - actual config_options has 4 items
    #         assert len(choices) == 4
    #
    @pytest.mark.asyncio
    async def test_config_autocomplete_no_matches(self, mock_bot: Bot, mock_interaction: Interaction) -> None:
        """Test autocomplete when no options match."""
        cog = Config(mock_bot)
        mock_config_options = [
            {"label": "Server Settings", "description": "Configure server"},
            {"label": "GitHub Settings", "description": "Configure GitHub"},
        ]

        with patch.object(cog, "config_options", mock_config_options):
            choices = await cog._config_autocomplete(mock_interaction, "nonexistent")

            # Should return empty list
            assert len(choices) == 0

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_config_rule_with_special_characters(self, mock_bot: Bot, mock_interaction: Interaction) -> None:
        """Test config_rule with special characters in setting."""
        cog = Config(mock_bot)
        mock_config_options = [
            {"label": "Server Settings", "description": "Configure server"},
        ]

        with patch.object(cog, "config_options", mock_config_options):
            callback = cog.config_rule.callback
            await callback(cog, mock_interaction, setting="@#$%^&*()")

            mock_interaction.response.send_message.assert_called_once()
            call_args = mock_interaction.response.send_message.call_args
            assert "Invalid setting" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_config_rule_view_creation_without_setting(
        self, mock_bot: Bot, mock_interaction: Interaction
    ) -> None:
        """Test config_rule creates view when no setting provided."""
        cog = Config(mock_bot)
        mock_config_options = [
            {"label": "Server Settings", "description": "Configure server"},
        ]

        with patch.object(cog, "config_options", mock_config_options):
            with patch("byte_bot.plugins.config.ConfigView") as mock_view_class:
                mock_view = MagicMock()
                mock_view_class.return_value = mock_view

                callback = cog.config_rule.callback
                await callback(cog, mock_interaction, setting=None)

                # Should create ConfigView without preselected option
                mock_view_class.assert_called_once_with()
                mock_interaction.response.send_message.assert_called_once()
                call_kwargs = mock_interaction.response.send_message.call_args[1]
                assert call_kwargs["view"] == mock_view

    @pytest.mark.asyncio
    async def test_config_rule_view_creation_with_valid_setting(
        self, mock_bot: Bot, mock_interaction: Interaction
    ) -> None:
        """Test config_rule creates view with preselected setting."""
        cog = Config(mock_bot)
        mock_config_options = [
            {"label": "Server Settings", "description": "Configure server"},
        ]

        with patch.object(cog, "config_options", mock_config_options):
            with patch("byte_bot.plugins.config.ConfigView") as mock_view_class:
                mock_view = MagicMock()
                mock_view_class.return_value = mock_view

                callback = cog.config_rule.callback
                await callback(cog, mock_interaction, setting="Server Settings")

                # Should create ConfigView with preselected option
                mock_view_class.assert_called_once_with(preselected="Server Settings")
                mock_interaction.response.send_message.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_config_cog_name_attribute(self, mock_bot: Bot) -> None:
        """Test Config cog has correct name attribute."""
        cog = Config(mock_bot)

        assert cog.__cog_name__ == "Config Commands"
