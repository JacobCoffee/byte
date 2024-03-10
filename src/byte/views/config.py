"""Discord UI views used in Byte config commands."""
from __future__ import annotations

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
        super().__init__(style=ButtonStyle.secondary, label="Finished")

    async def callback(self, interaction: Interaction) -> None:
        """Callback for button.

        Args:
            interaction: Interaction object.
        """
        await interaction.response.send_message("Configuration complete!", ephemeral=True)
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
        selected_option = self.values[0]
        modal = ConfigModal(title=f"Configure {selected_option}")
        await interaction.response.send_modal(modal)
        await interaction.followup.send_message("Select another setting or click 'Finished' when done.", ephemeral=True)
        self.view.stop()


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


class ConfigModal(Modal):
    """Configuration modal."""

    def __init__(self, title: str) -> None:
        """Initialize modal.

        Args:
            title: Title of modal.
        """
        super().__init__(title=title)
        self.add_item(
            TextInput(
                label="Configuration Value",
                style=TextStyle.short,
                placeholder="Enter your configuration here...",
                required=True,
            )
        )

    async def callback(self, interaction: Interaction) -> None:
        """Callback for modal.

        Args:
            interaction: Interaction object.
        """
        config_value = self.children[0].value
        await interaction.response.send_message(f"Configuration value received!: {config_value}", ephemeral=True)
        view = ConfigView()
        await interaction.followup.send_message(
            "Select another setting or click 'Finished' when done.", view=view, ephemeral=True
        )
