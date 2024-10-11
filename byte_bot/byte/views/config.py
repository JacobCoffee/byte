"""Discord UI views used in Byte config commands."""

from __future__ import annotations

from typing import Any

from discord import ButtonStyle, Interaction, SelectOption, TextStyle
from discord.ui import Button, Modal, Select, TextInput, View

from byte.lib.common import config_options
from byte.lib.log import get_logger

__all__ = ("ConfigView",)

logger = get_logger()


class FinishButton(Button):
    """Finish button."""

    def __init__(self) -> None:
        """Initialize button."""
        super().__init__(style=ButtonStyle.success, label="Finished")

    async def callback(self, interaction: Interaction) -> None:
        """Callback for button.

        Args:
            interaction: Interaction object.
        """
        await interaction.response.send_message("Configuration complete!", ephemeral=True)
        self.view.stop()


class BackButton(Button):
    """Back button."""

    def __init__(self) -> None:
        """Initialize button."""
        super().__init__(style=ButtonStyle.secondary, label="Back")

    async def callback(self, interaction: Interaction) -> None:
        """Callback for button.

        Args:
            interaction: Interaction object.
        """
        view = ConfigView()
        await interaction.response.edit_message(content="Select a configuration option:", view=view)


class CancelButton(Button):
    """Cancel button."""

    def __init__(self) -> None:
        """Initialize button."""
        super().__init__(style=ButtonStyle.danger, label="Cancel")

    async def callback(self, interaction: Interaction) -> None:
        """Callback for button.

        Args:
            interaction: Interaction object.
        """
        await interaction.response.send_message("Configuration cancelled.", ephemeral=True)
        self.view.stop()


class ConfigSelect(Select):
    """Configuration select dropdown menu."""

    def __init__(self, preselected: str | None = None) -> None:
        """Initialize select.

        Args:
            preselected: Preselected option, if given.
        """
        options = [SelectOption(label=option["label"], description=option["description"]) for option in config_options]
        super().__init__(placeholder="Choose a setting...", min_values=1, max_values=1, options=options)

        if preselected:
            for option in options:
                if option.label == preselected:
                    option.default = True
                    break

    async def callback(self, interaction: Interaction) -> None:
        """Callback for select.

        Args:
            interaction: Interaction object.
        """
        selected_option = next(option for option in config_options if option["label"] == self.values[0])
        if "sub_settings" in selected_option:
            view = ConfigKeyView(selected_option)
            await interaction.response.edit_message(content=f"Select a key for {selected_option['label']}:", view=view)
        else:
            modal = ConfigModal(title=f"Configure {selected_option['label']}")
            await interaction.response.send_modal(modal)


class ConfigKeySelect(Select):
    """Configuration key select dropdown menu."""

    def __init__(self, option: dict[str, Any]) -> None:
        """Initialize select.

        Args:
            option: The selected configuration option.
        """
        self.option = option
        options = [
            SelectOption(label=sub_setting["label"], description=sub_setting.get("description", ""))
            for sub_setting in option["sub_settings"]
        ]
        super().__init__(placeholder="Choose a key...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction) -> None:
        """Callback for select.

        Args:
            interaction: Interaction object.
        """
        selected_sub_setting = self.values[0]
        selected_sub_setting = next(
            sub_setting for sub_setting in self.option["sub_settings"] if sub_setting["label"] == selected_sub_setting
        )
        modal = ConfigModal(
            title=f"{self.option['label']} - {selected_sub_setting['label']}",
            sub_setting=selected_sub_setting,
            option=self.option,
        )
        await interaction.response.send_modal(modal)


class ConfigView(View):
    """Configuration view."""

    def __init__(self, preselected: str | None = None) -> None:
        """Initialize view.

        Args:
            preselected: Preselected option, if given.
        """
        super().__init__(timeout=None)
        self.add_item(ConfigSelect(preselected))
        self.add_item(FinishButton())
        self.add_item(CancelButton())


class ConfigKeyView(View):
    """Configuration key view."""

    def __init__(self, option: dict[str, Any]) -> None:
        """Initialize view.

        Args:
            option: The selected configuration option.
        """
        super().__init__(timeout=None)
        self.add_item(ConfigKeySelect(option))
        self.add_item(BackButton())
        self.add_item(CancelButton())


class ConfigModal(Modal):
    """Configuration modal."""

    def __init__(
        self,
        title: str,
        sub_setting: dict[str, str] | None = None,
        sub_settings: list[dict[str, str]] | None = None,
        option: dict[str, Any] | None = None,
    ) -> None:
        """Initialize modal.

        Args:
            title: Title of modal.
            sub_setting: The selected sub-setting, if applicable.
            sub_settings: List of sub-settings, if configuring all keys.
            option: The selected configuration option, if applicable.
        """
        super().__init__(title=title + "\n\n")
        self.option = option

        if sub_settings:
            for _sub_setting in sub_settings:
                self.add_item(
                    TextInput(
                        label=_sub_setting["label"],
                        style=TextStyle.short,
                        custom_id=_sub_setting["field"],
                        placeholder=f"Enter {_sub_setting['label']} ({_sub_setting['data_type']})",
                        required=True,
                        min_length=4 if _sub_setting["data_type"] == "True/False" else 1,
                        max_length=5
                        if _sub_setting["data_type"] == "True/False"
                        else 100
                        if _sub_setting["data_type"] in ["String", "Integer"]
                        else 300
                        if _sub_setting["data_type"] == "Comma-separated list"
                        else None,
                    )
                )
        elif sub_setting:
            self.add_item(
                TextInput(
                    label=sub_setting["label"],
                    style=TextStyle.short,
                    placeholder=f"Enter {sub_setting['label']} ({sub_setting['data_type']})",
                    required=True,
                    min_length=4 if sub_setting["data_type"] == "True/False" else 1,
                    max_length=5
                    if sub_setting["data_type"] == "True/False"
                    else 100
                    if sub_setting["data_type"] in ["String", "Integer"]
                    else 300
                    if sub_setting["data_type"] == "Comma-separated list"
                    else None,
                )
            )
        else:
            self.add_item(
                TextInput(
                    label="Configuration Value",
                    style=TextStyle.short,
                    placeholder="Enter your configuration value...",
                    required=True,
                )
            )

    async def on_submit(self, interaction: Interaction) -> None:
        """Handle modal submission.

        Args:
            interaction: Interaction object.
        """
        config_values = {item.custom_id: item.value for item in self.children if hasattr(item, "custom_id")}
        await interaction.response.send_message(f"Configuration values received: {config_values}", ephemeral=True)

        if self.option:
            view = ConfigKeyView(self.option)
            await interaction.followup.send(
                f"Select another key for {self.option['label']} or click 'Back' to return to the main menu.",
                view=view,
                ephemeral=True,
            )
        else:
            view = ConfigView()
            await interaction.followup.send(
                "Select another setting or click 'Finished' when done.", view=view, ephemeral=True
            )

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        """Handle modal submission error.

        Args:
            interaction: Interaction object.
            error: Error object.
        """
        await interaction.response.send_message("Oops! Something went wrong.", ephemeral=True)
        logger.exception("Error occurred while processing config modal submission", exc_info=error)
