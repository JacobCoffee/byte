"""Discord UI views used in forums."""

from discord import ButtonStyle, Interaction
from discord.ext.commands import Bot
from discord.ui import Button, View, button
from sqlalchemy import select

from byte.lib.log import get_logger
from server.domain.db.models import Guild
from server.lib.db import config

__all__ = ("HelpThreadView",)

logger = get_logger()


class HelpThreadView(View):
    """View for the help thread."""

    def __init__(self, author: Interaction.user, guild_id: int, bot: Bot, *args: list, **kwargs: dict) -> None:
        """Initialize the view."""
        super().__init__(*args, **kwargs)
        self.author = author
        self.bot = bot
        self.guild_id = guild_id

    async def setup(self) -> None:
        """Asynchronously setup guild details and add button.

        .. todo:: Think about this more - If we plan on decoupling this
            should be a call to an endpoint like we do in ``byte.bot.Byte.on_guild_join``.
        """
        # noinspection PyBroadException
        try:
            async with config.get_session() as session:
                stmt = select(Guild).where(Guild.guild_id == self.guild_id)
                result = await session.execute(stmt)
                guild_settings = result.scalars().first()

            if guild_settings and guild_settings.github_config:
                guild_repo = guild_settings.github_config.github_repository
                self.add_item(
                    Button(label="Open GitHub Issue", style=ButtonStyle.blurple, url=f"{guild_repo}/new/choose")
                )
            else:
                logger.warning("no github configuration found for guild %s", self.guild_id)
                await self.author.send("No GitHub configuration found for this guild. Please contact an admin.")
        except Exception:
            logger.exception("failed to setup view for guild %s", self.guild_id)

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Check if the user is the author or an admin.

        Args:
            interaction (Interaction): Interaction object.

        Returns:
            bool: True if the user is the author or an admin, False otherwise.
        """
        return interaction.user == self.author or interaction.user.guild_permissions.administrator

    @button(label="Solve", style=ButtonStyle.green, custom_id="solve_button")
    async def solve_button_callback(self, interaction: Interaction, button: Button) -> None:  # noqa: ARG002
        """Mark the thread as solved.

        Args:
            interaction: Interaction object.
            button: Button object.
        """
        await interaction.response.defer()

        ctx = await self.bot.get_context(interaction.message)
        solve_command = self.bot.get_command("solve")
        if solve_command is not None:
            ctx.command = solve_command
            ctx.invoked_with = "solve"
            ctx.args.append(ctx)
            logger.info(
                "invoking solve command for %s by %s on thread %s", ctx.channel, interaction.user, interaction.channel
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
        content = interaction.message.content or "\u200b"
        logger.info("removing view for %s by %s", interaction.channel, interaction.user)
        await interaction.message.edit(content=content, embed=None, view=None)
