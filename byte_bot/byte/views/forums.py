"""Discord UI views used in forums."""

from discord import ButtonStyle, Interaction, Member
from discord.ext.commands import Bot
from discord.ui import Button, View, button

from byte_bot.byte.lib.common.links import litestar_issues
from byte_bot.byte.lib.log import get_logger

__all__ = ("HelpThreadView",)


logger = get_logger()


class HelpThreadView(View):
    """View for the help thread."""

    def __init__(self, author: Member, bot: Bot, *args: list, **kwargs: dict) -> None:
        """Initialize the view."""
        super().__init__(*args, **kwargs)
        self.author = author
        self.bot = bot

        self.add_item(Button(label="Open GitHub Issue", style=ButtonStyle.blurple, url=f"{litestar_issues}/new/choose"))

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Check if the user is the author or an admin.

        Args:
            interaction (Interaction): Interaction object.

        Returns:
            bool: True if the user is the author or an admin, False otherwise.
        """
        return interaction.user == self.author or (
            hasattr(interaction.user, "guild_permissions") and interaction.user.guild_permissions.administrator  # type: ignore[attr-defined]
        )

    @button(label="Solve", style=ButtonStyle.green, custom_id="solve_button")
    async def solve_button_callback(self, interaction: Interaction, button: Button) -> None:  # noqa: ARG002
        """Mark the thread as solved.

        Args:
            interaction: Interaction object.
            button: Button object.
        """
        await interaction.response.defer()

        if interaction.message:
            ctx = await self.bot.get_context(interaction.message)
            solve_command = self.bot.get_command("solve")
            if solve_command is not None:
                ctx.command = solve_command
                ctx.invoked_with = "solve"
                ctx.args.append(ctx)
                logger.info(
                    "invoking solve command for %s by %s on thread %s",
                    ctx.channel,
                    interaction.user,
                    interaction.channel,
                )

                try:
                    await solve_command.invoke(ctx)
                    await interaction.followup.send("Marked as solved and closed the help forum!", ephemeral=True)
                except Exception:
                    logger.exception("failed to invoke solve command")
                    await interaction.followup.send("Failed to mark as solved. Please try again.", ephemeral=True)

    @button(label="Remove", style=ButtonStyle.red, custom_id="remove_button")
    async def remove_button_callback(self, interaction: Interaction, button: Button) -> None:  # noqa: ARG002
        """Remove the view and embed.

        Args:
            interaction: Interaction object.
            button: Button object.
        """
        if interaction.message:
            content = interaction.message.content or "\u200b"
            logger.info("removing view for %s by %s", interaction.channel, interaction.user)
            await interaction.message.edit(content=content, embed=None, view=None)
