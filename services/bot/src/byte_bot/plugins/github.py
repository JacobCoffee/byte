"""Plugins for GitHub interactions."""

from __future__ import annotations

from discord import Interaction, Message, TextStyle, app_commands
from discord.ext.commands import Bot, Cog
from discord.ui import Modal, TextInput
from discord.utils import MISSING

# TODO: Implement GitHub client for bot service
# from byte_common.clients.github import create_github_client

__all__ = ("GitHubCommands", "setup")


class GitHubIssue(Modal, title="Create GitHub Issue"):
    """Modal for GitHub issue creation."""

    title_ = TextInput(label="title", placeholder="Title")
    description = TextInput(
        label="Description",
        style=TextStyle.paragraph,
        placeholder="Please enter an description of the bug you are encountering.",
    )
    mcve = TextInput(
        label="MCVE",
        style=TextStyle.paragraph,
        placeholder="Please provide a minimal, complete, and verifiable example of the issue.",
    )
    logs = TextInput(
        label="Logs", style=TextStyle.paragraph, placeholder="Please copy and paste any relevant log output."
    )
    version = TextInput(
        label="Project Version", placeholder="What version of the project are you using when encountering this issue?"
    )

    def __init__(
        self,
        *,
        title: str = MISSING,
        timeout: float | None = None,
        custom_id: str = MISSING,
        message: Message | None = None,
    ) -> None:
        # NOTE: check how else to set default
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        if message:
            self.description.default = message.content

    async def on_submit(self, interaction: Interaction) -> None:
        # issue_reporter = interaction.user
        # TODO: Uncomment when GitHub client is implemented
        # issue_body_lines = [
        #     "### Reported by",
        #     f"[{issue_reporter.display_name}](https://discord.com/users/{issue_reporter.id}) in Discord: {getattr(interaction.channel, 'name', 'DM')}",  # noqa: E501
        #     "",
        #     "### Description",
        #     f"{self.description.value.strip()}",
        #     "",
        #     "### MCVE",
        #     f"{self.mcve.value.strip()}",
        #     "",
        #     "### Logs",
        #     f"{self.logs.value.strip()}",
        #     "",
        #     "### Project Version",
        #     f"{self.version.value.strip()}",
        # ]
        # issue_body = "\n".join(issue_body_lines)
        try:
            # TODO: Implement GitHub client for bot service
            # response_wrapper = await github_client.rest.issues.async_create(
            #     owner="litestar-org", repo="litestar", data={"title": self.title_.value, "body": issue_body}
            # )
            # if codes.is_success(response_wrapper.status_code):
            #     await interaction.response.send_message(
            #         f"GitHub Issue created: {response_wrapper.parsed_data.html_url}", ephemeral=False
            #     )
            # else:
            #     await interaction.response.send_message("Issue creation failed.", ephemeral=True)
            await interaction.response.send_message(
                "GitHub issue creation is temporarily disabled during service migration.", ephemeral=True
            )
        except Exception as e:  # noqa: BLE001
            await interaction.response.send_message(f"An error occurred: {e!s}", ephemeral=True)


class GitHubCommands(Cog):
    """GitHub command cog."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "GitHub Commands"  # type: ignore[misc]
        self.context_menu = app_commands.ContextMenu(
            # TODO: Name changed to not conflict with the other one, discord shows both
            name="Create GitHub Issue",
            callback=self.create_github_issue_modal,
        )
        bot.tree.add_command(self.context_menu)

    async def create_github_issue_modal(self, interaction: Interaction, message: Message) -> None:
        """Context menu command to create a GitHub issue from a Discord message.

        Args:
            interaction: Interaction object.
            message: Message object.
        """
        await interaction.response.send_modal(GitHubIssue(message=message))


async def setup(bot: Bot) -> None:
    """Add cog to bot.

    Args:
        bot: Bot object.
    """
    await bot.add_cog(GitHubCommands(bot))
