"""Tests for config views module."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from byte_bot.views.config import (
    BackButton,
    CancelButton,
    ConfigKeySelect,
    ConfigKeyView,
    ConfigModal,
    ConfigSelect,
    ConfigView,
    FinishButton,
)

if TYPE_CHECKING:
    from discord import Interaction


@pytest.fixture
def mock_config_options() -> list[dict]:
    """Mock config options."""
    return [
        {
            "label": "Server Settings",
            "description": "Configure server settings",
            "sub_settings": [
                {"label": "Prefix", "field": "prefix", "data_type": "String"},
                {"label": "Help Channel", "field": "help_channel_id", "data_type": "Integer"},
            ],
        },
        {
            "label": "GitHub Settings",
            "description": "Configure GitHub",
        },
    ]


class TestFinishButton:
    """Tests for FinishButton."""

    @pytest.mark.asyncio
    async def test_finish_button_initialization(self) -> None:
        """Test FinishButton initializes correctly."""
        button = FinishButton()

        assert button.label == "Finished"
        assert button.style.name == "success"

    @pytest.mark.asyncio
    async def test_finish_button_has_callback(self) -> None:
        """Test FinishButton has callback method."""
        button = FinishButton()

        assert hasattr(button, "callback")
        assert callable(button.callback)


class TestBackButton:
    """Tests for BackButton."""

    @pytest.mark.asyncio
    async def test_back_button_initialization(self) -> None:
        """Test BackButton initializes correctly."""
        button = BackButton()

        assert button.label == "Back"
        assert button.style.name == "secondary"

    @pytest.mark.asyncio
    async def test_back_button_callback(self, mock_interaction: Interaction) -> None:
        """Test BackButton callback creates new ConfigView."""
        button = BackButton()

        mock_interaction.response.edit_message = AsyncMock()

        await button.callback(mock_interaction)

        mock_interaction.response.edit_message.assert_called_once()
        call_kwargs = mock_interaction.response.edit_message.call_args[1]
        assert "configuration" in call_kwargs["content"].lower()
        assert isinstance(call_kwargs["view"], ConfigView)


class TestCancelButton:
    """Tests for CancelButton."""

    @pytest.mark.asyncio
    async def test_cancel_button_initialization(self) -> None:
        """Test CancelButton initializes correctly."""
        button = CancelButton()

        assert button.label == "Cancel"
        assert button.style.name == "danger"

    @pytest.mark.asyncio
    async def test_cancel_button_has_callback(self) -> None:
        """Test CancelButton has callback method."""
        button = CancelButton()

        assert hasattr(button, "callback")
        assert callable(button.callback)


class TestConfigSelect:
    """Tests for ConfigSelect."""

    @pytest.mark.asyncio
    async def test_config_select_initialization(self, mock_config_options: list[dict]) -> None:
        """Test ConfigSelect initializes with options."""
        with patch("byte_bot.views.config.config_options", mock_config_options):
            select = ConfigSelect()

            assert select.placeholder == "Choose a setting..."
            assert select.min_values == 1
            assert select.max_values == 1
            assert len(select.options) == len(mock_config_options)

    @pytest.mark.asyncio
    async def test_config_select_with_preselected(self, mock_config_options: list[dict]) -> None:
        """Test ConfigSelect with preselected option."""
        with patch("byte_bot.views.config.config_options", mock_config_options):
            select = ConfigSelect(preselected="Server Settings")

            # Find the preselected option
            preselected_option = next(opt for opt in select.options if opt.label == "Server Settings")
            assert preselected_option.default is True

    @pytest.mark.asyncio
    async def test_config_select_has_callback(self, mock_config_options: list[dict]) -> None:
        """Test ConfigSelect has callback method."""
        with patch("byte_bot.views.config.config_options", mock_config_options):
            select = ConfigSelect()

            assert hasattr(select, "callback")
            assert callable(select.callback)


class TestConfigKeySelect:
    """Tests for ConfigKeySelect."""

    @pytest.mark.asyncio
    async def test_config_key_select_initialization(self, mock_config_options: list[dict]) -> None:
        """Test ConfigKeySelect initializes with sub_settings."""
        option = mock_config_options[0]
        select = ConfigKeySelect(option)

        assert select.option == option
        assert select.placeholder == "Choose a key..."
        assert len(select.options) == len(option["sub_settings"])

    @pytest.mark.asyncio
    async def test_config_key_select_has_callback(self, mock_config_options: list[dict]) -> None:
        """Test ConfigKeySelect has callback method."""
        option = mock_config_options[0]
        select = ConfigKeySelect(option)

        assert hasattr(select, "callback")
        assert callable(select.callback)


class TestConfigView:
    """Tests for ConfigView."""

    @pytest.mark.asyncio
    async def test_config_view_initialization(self, mock_config_options: list[dict]) -> None:
        """Test ConfigView initializes with all components."""
        with patch("byte_bot.views.config.config_options", mock_config_options):
            view = ConfigView()

            assert view.timeout is None
            # Should have ConfigSelect, FinishButton, CancelButton
            assert len(view.children) == 3

    @pytest.mark.asyncio
    async def test_config_view_with_preselected(self, mock_config_options: list[dict]) -> None:
        """Test ConfigView with preselected option."""
        with patch("byte_bot.views.config.config_options", mock_config_options):
            view = ConfigView(preselected="Server Settings")

            # ConfigSelect should be first child
            config_select = view.children[0]
            assert isinstance(config_select, ConfigSelect)


class TestConfigKeyView:
    """Tests for ConfigKeyView."""

    @pytest.mark.asyncio
    async def test_config_key_view_initialization(self, mock_config_options: list[dict]) -> None:
        """Test ConfigKeyView initializes with sub-setting selector."""
        option = mock_config_options[0]
        view = ConfigKeyView(option)

        assert view.timeout is None
        # Should have ConfigKeySelect, BackButton, CancelButton
        assert len(view.children) == 3

    @pytest.mark.asyncio
    async def test_config_key_view_has_back_button(self, mock_config_options: list[dict]) -> None:
        """Test ConfigKeyView includes BackButton."""
        option = mock_config_options[0]
        view = ConfigKeyView(option)

        # BackButton should be second child
        back_button = view.children[1]
        assert isinstance(back_button, BackButton)


class TestConfigModal:
    """Tests for ConfigModal."""

    @pytest.mark.asyncio
    async def test_config_modal_initialization_simple(self) -> None:
        """Test ConfigModal initializes without sub_settings."""
        modal = ConfigModal(title="Test Config")

        assert "Test Config" in modal.title
        assert len(modal.children) == 1

    @pytest.mark.asyncio
    async def test_config_modal_initialization_with_sub_setting(self) -> None:
        """Test ConfigModal initializes with a single sub_setting."""
        sub_setting = {"label": "Prefix", "field": "prefix", "data_type": "String"}
        modal = ConfigModal(title="Test", sub_setting=sub_setting)

        assert len(modal.children) == 1
        text_input = modal.children[0]
        assert text_input.label == "Prefix"  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_config_modal_initialization_with_sub_settings_list(self) -> None:
        """Test ConfigModal initializes with multiple sub_settings."""
        sub_settings = [
            {"label": "Prefix", "field": "prefix", "data_type": "String"},
            {"label": "Channel", "field": "channel_id", "data_type": "Integer"},
        ]
        modal = ConfigModal(title="Test", sub_settings=sub_settings)

        assert len(modal.children) == 2

    @pytest.mark.asyncio
    async def test_config_modal_on_submit(self, mock_interaction: Interaction) -> None:
        """Test ConfigModal on_submit handles submission."""
        modal = ConfigModal(title="Test")

        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        # Modal already has a TextInput child from initialization
        await modal.on_submit(mock_interaction)

        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert "received" in call_args[0][0].lower()

        # Should send followup with new view
        mock_interaction.followup.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_config_modal_on_submit_with_option(
        self, mock_interaction: Interaction, mock_config_options: list[dict]
    ) -> None:
        """Test ConfigModal on_submit with option returns to ConfigKeyView."""
        option = mock_config_options[0]
        modal = ConfigModal(title="Test", option=option)

        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        await modal.on_submit(mock_interaction)

        # Should send ConfigKeyView in followup
        call_kwargs = mock_interaction.followup.send.call_args[1]
        assert isinstance(call_kwargs["view"], ConfigKeyView)

    @pytest.mark.asyncio
    async def test_config_modal_on_error(self, mock_interaction: Interaction) -> None:
        """Test ConfigModal on_error handles errors."""
        modal = ConfigModal(title="Test")

        error = Exception("Test error")
        await modal.on_error(mock_interaction, error)

        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert "wrong" in call_args[0][0].lower()
        assert call_args[1]["ephemeral"] is True

    @pytest.mark.asyncio
    async def test_config_modal_text_input_data_type_boolean(self) -> None:
        """Test ConfigModal creates correct TextInput for True/False data type."""
        sub_setting = {"label": "Enabled", "field": "enabled", "data_type": "True/False"}
        modal = ConfigModal(title="Test", sub_setting=sub_setting)

        text_input = modal.children[0]
        assert text_input.min_length == 4  # type: ignore[attr-defined]
        assert text_input.max_length == 5  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_config_modal_text_input_data_type_string(self) -> None:
        """Test ConfigModal creates correct TextInput for String data type."""
        sub_setting = {"label": "Name", "field": "name", "data_type": "String"}
        modal = ConfigModal(title="Test", sub_setting=sub_setting)

        text_input = modal.children[0]
        assert text_input.min_length == 1  # type: ignore[attr-defined]
        assert text_input.max_length == 100  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_config_modal_text_input_data_type_integer(self) -> None:
        """Test ConfigModal creates correct TextInput for Integer data type."""
        sub_setting = {"label": "Count", "field": "count", "data_type": "Integer"}
        modal = ConfigModal(title="Test", sub_setting=sub_setting)

        text_input = modal.children[0]
        assert text_input.max_length == 100  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_config_modal_text_input_data_type_comma_separated(self) -> None:
        """Test ConfigModal creates correct TextInput for comma-separated list."""
        sub_setting = {"label": "Tags", "field": "tags", "data_type": "Comma-separated list"}
        modal = ConfigModal(title="Test", sub_setting=sub_setting)

        text_input = modal.children[0]
        assert text_input.max_length == 300  # type: ignore[attr-defined]


class TestFinishButtonCallbacks:
    """Tests for FinishButton callback behavior."""

    @pytest.mark.asyncio
    async def test_finish_button_callback_sends_message(self, mock_interaction: Interaction) -> None:
        """Test FinishButton callback sends completion message."""
        button = FinishButton()
        # Create a mock view and patch the view property
        mock_view = MagicMock()
        mock_view.stop = MagicMock()

        with patch.object(type(button), "view", new_callable=lambda: property(lambda self: mock_view)):
            await button.callback(mock_interaction)

            mock_interaction.response.send_message.assert_called_once()
            call_args = mock_interaction.response.send_message.call_args
            assert "complete" in call_args[0][0].lower()
            assert call_args[1]["ephemeral"] is True
            mock_view.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_finish_button_callback_no_view(self, mock_interaction: Interaction) -> None:
        """Test FinishButton callback handles missing view gracefully."""
        button = FinishButton()

        with patch.object(type(button), "view", new_callable=lambda: property(lambda self: None)):
            await button.callback(mock_interaction)

            mock_interaction.response.send_message.assert_called_once()


class TestCancelButtonCallbacks:
    """Tests for CancelButton callback behavior."""

    @pytest.mark.asyncio
    async def test_cancel_button_callback_sends_message(self, mock_interaction: Interaction) -> None:
        """Test CancelButton callback sends cancellation message."""
        button = CancelButton()
        mock_view = MagicMock()
        mock_view.stop = MagicMock()

        with patch.object(type(button), "view", new_callable=lambda: property(lambda self: mock_view)):
            await button.callback(mock_interaction)

            mock_interaction.response.send_message.assert_called_once()
            call_args = mock_interaction.response.send_message.call_args
            assert "cancel" in call_args[0][0].lower()
            assert call_args[1]["ephemeral"] is True
            mock_view.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_button_callback_no_view(self, mock_interaction: Interaction) -> None:
        """Test CancelButton callback handles missing view gracefully."""
        button = CancelButton()

        with patch.object(type(button), "view", new_callable=lambda: property(lambda self: None)):
            await button.callback(mock_interaction)

            mock_interaction.response.send_message.assert_called_once()


class TestConfigSelectCallbacks:
    """Tests for ConfigSelect callback behavior."""

    @pytest.mark.asyncio
    async def test_config_select_callback_with_sub_settings(
        self, mock_interaction: Interaction, mock_config_options: list[dict]
    ) -> None:
        """Test ConfigSelect callback opens ConfigKeyView for options with sub_settings."""
        with patch("byte_bot.views.config.config_options", mock_config_options):
            select = ConfigSelect()

            mock_interaction.response.edit_message = AsyncMock()

            with patch.object(type(select), "values", new_callable=lambda: property(lambda self: ["Server Settings"])):
                await select.callback(mock_interaction)

                mock_interaction.response.edit_message.assert_called_once()
                call_kwargs = mock_interaction.response.edit_message.call_args[1]
                assert isinstance(call_kwargs["view"], ConfigKeyView)
                assert "server settings" in call_kwargs["content"].lower()

    @pytest.mark.asyncio
    async def test_config_select_callback_without_sub_settings(
        self, mock_interaction: Interaction, mock_config_options: list[dict]
    ) -> None:
        """Test ConfigSelect callback opens modal for options without sub_settings."""
        with patch("byte_bot.views.config.config_options", mock_config_options):
            select = ConfigSelect()

            mock_interaction.response.send_modal = AsyncMock()

            with patch.object(type(select), "values", new_callable=lambda: property(lambda self: ["GitHub Settings"])):
                await select.callback(mock_interaction)

                mock_interaction.response.send_modal.assert_called_once()
                modal = mock_interaction.response.send_modal.call_args[0][0]
                assert isinstance(modal, ConfigModal)
                assert "GitHub Settings" in modal.title


class TestConfigKeySelectCallbacks:
    """Tests for ConfigKeySelect callback behavior."""

    @pytest.mark.asyncio
    async def test_config_key_select_callback_opens_modal(
        self, mock_interaction: Interaction, mock_config_options: list[dict]
    ) -> None:
        """Test ConfigKeySelect callback opens modal for selected key."""
        option = mock_config_options[0]
        select = ConfigKeySelect(option)

        mock_interaction.response.send_modal = AsyncMock()

        with patch.object(type(select), "values", new_callable=lambda: property(lambda self: ["Prefix"])):
            await select.callback(mock_interaction)

            mock_interaction.response.send_modal.assert_called_once()
            modal = mock_interaction.response.send_modal.call_args[0][0]
            assert isinstance(modal, ConfigModal)
            assert "Server Settings" in modal.title
            assert "Prefix" in modal.title

    @pytest.mark.asyncio
    async def test_config_key_select_callback_preserves_option(
        self, mock_interaction: Interaction, mock_config_options: list[dict]
    ) -> None:
        """Test ConfigKeySelect callback preserves option context in modal."""
        option = mock_config_options[0]
        select = ConfigKeySelect(option)

        mock_interaction.response.send_modal = AsyncMock()

        with patch.object(type(select), "values", new_callable=lambda: property(lambda self: ["Help Channel"])):
            await select.callback(mock_interaction)

            modal = mock_interaction.response.send_modal.call_args[0][0]
            assert modal.option == option


class TestConfigModalSubmission:
    """Tests for ConfigModal submission handling."""

    @pytest.mark.asyncio
    async def test_config_modal_submission_extracts_values(self, mock_interaction: Interaction) -> None:
        """Test ConfigModal on_submit extracts values from text inputs."""
        sub_setting = {"label": "Prefix", "field": "prefix", "data_type": "String"}
        modal = ConfigModal(title="Test", sub_setting=sub_setting)

        # Mock the text input children
        text_input = modal.children[0]

        with (
            patch.object(type(text_input), "custom_id", new="prefix"),
            patch.object(type(text_input), "value", new_callable=lambda: property(lambda self: "!")),
        ):
            mock_interaction.followup = MagicMock()
            mock_interaction.followup.send = AsyncMock()

            await modal.on_submit(mock_interaction)

            # Check that values were extracted
            mock_interaction.response.send_message.assert_called_once()
            call_args = mock_interaction.response.send_message.call_args[0][0]
            assert "prefix" in call_args.lower()

    @pytest.mark.asyncio
    async def test_config_modal_submission_returns_to_main(self, mock_interaction: Interaction) -> None:
        """Test ConfigModal on_submit returns to main ConfigView when no option."""
        modal = ConfigModal(title="Test", option=None)

        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()

        await modal.on_submit(mock_interaction)

        # Should send ConfigView
        call_kwargs = mock_interaction.followup.send.call_args[1]
        assert isinstance(call_kwargs["view"], ConfigView)
        assert call_kwargs["ephemeral"] is True

    @pytest.mark.asyncio
    async def test_config_modal_submission_multiple_inputs(self, mock_interaction: Interaction) -> None:
        """Test ConfigModal on_submit handles multiple text inputs."""
        sub_settings = [
            {"label": "Prefix", "field": "prefix", "data_type": "String"},
            {"label": "Channel", "field": "channel_id", "data_type": "Integer"},
        ]
        modal = ConfigModal(title="Test", sub_settings=sub_settings)

        # Mock the text input children
        text_input_0 = modal.children[0]
        text_input_1 = modal.children[1]

        with (
            patch.object(type(text_input_0), "custom_id", new="prefix"),
            patch.object(type(text_input_0), "value", new_callable=lambda: property(lambda self: "!")),
            patch.object(type(text_input_1), "custom_id", new="channel_id"),
            patch.object(type(text_input_1), "value", new_callable=lambda: property(lambda self: "123456")),
        ):
            mock_interaction.followup = MagicMock()
            mock_interaction.followup.send = AsyncMock()

            await modal.on_submit(mock_interaction)

            mock_interaction.response.send_message.assert_called_once()


class TestConfigModalErrorHandling:
    """Tests for ConfigModal error handling."""

    @pytest.mark.asyncio
    async def test_config_modal_on_error_logs_exception(self, mock_interaction: Interaction) -> None:
        """Test ConfigModal on_error sends error message."""
        modal = ConfigModal(title="Test")
        error = ValueError("Invalid value")

        with patch("byte_bot.views.config.logger") as mock_logger:
            await modal.on_error(mock_interaction, error)

            mock_logger.exception.assert_called_once()
            mock_interaction.response.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_config_modal_on_error_message_ephemeral(self, mock_interaction: Interaction) -> None:
        """Test ConfigModal on_error sends ephemeral message."""
        modal = ConfigModal(title="Test")
        error = RuntimeError("Test error")

        await modal.on_error(mock_interaction, error)

        call_args = mock_interaction.response.send_message.call_args
        assert call_args[1]["ephemeral"] is True


class TestConfigViewTimeout:
    """Tests for ConfigView timeout behavior."""

    @pytest.mark.asyncio
    async def test_config_view_no_timeout(self, mock_config_options: list[dict]) -> None:
        """Test ConfigView is created without timeout."""
        with patch("byte_bot.views.config.config_options", mock_config_options):
            view = ConfigView()

            assert view.timeout is None

    @pytest.mark.asyncio
    async def test_config_key_view_no_timeout(self, mock_config_options: list[dict]) -> None:
        """Test ConfigKeyView is created without timeout."""
        option = mock_config_options[0]
        view = ConfigKeyView(option)

        assert view.timeout is None
