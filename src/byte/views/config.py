"""Discord UI views used in Byte config commands."""
from __future__ import annotations

from discord import ButtonStyle, Interaction, SelectOption, TextStyle
from discord.ui import Button, Modal, Select, TextInput, View

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

    def __init__(self) -> None:
        """Initialize options."""
        options = [
            SelectOption(label="Server Settings", description="Configure overall server settings"),
            SelectOption(label="Forum Settings", description="Configure help and showcase forum settings"),
            SelectOption(label="GitHub Settings", description="Configure GitHub settings"),
            SelectOption(label="StackOverflow Settings", description="Configure StackOverflow settings"),
            SelectOption(label="Allowed Users", description="Configure allowed users"),
            SelectOption(label="Byte", description="Configure meta Byte features and settings"),

        ]
        super().__init__(placeholder="Choose a setting...", min_values=1, max_values=1, options=options)

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

    def __init__(self) -> None:
        """Initialize view."""
        super().__init__(timeout=None)
        self.add_item(ConfigSelect())
        self.add_item(FinishButton())


class ConfigModal(Modal):
    """Configuration modal."""

    def __init__(self, title: str) -> None:
        """Initialize modal.

        Args:
            title: Title of modal.
        """
        super().__init__(title=title)
        self.add_item(TextInput(
            label="Configuration Value",
            style=TextStyle.short,
            placeholder="Enter your configuration here...",
            required=True
        ))

    async def callback(self, interaction: Interaction) -> None:
        """Callback for modal.

        Args:
            interaction: Interaction object.
        """
        config_value = self.children[0].value
        await interaction.response.send_message(f"Configuration value received!: {config_value}", ephemeral=True)
        view = ConfigView()
        await interaction.followup.send_message("Select another setting or click 'Finished' when done.", view=view,
                                                ephemeral=True)
