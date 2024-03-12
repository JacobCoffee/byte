"""Custom plugins for the Litestar Discord."""
from __future__ import annotations

from typing import Literal, Self, cast

from discord import Embed, Interaction, Message, TextStyle, app_commands
from discord.ext.commands import Bot, Cog, Context, command, group, is_owner
from discord.ui import Modal, TextInput
from discord.utils import MISSING
from httpx import codes
from pydantic import AnyUrl, TypeAdapter, ValidationError

from byte.lib.utils import is_byte_dev, mention_role, mention_user
from server.domain.github.helpers import github_client

__all__ = ("LitestarCommands", "setup")


class GitHubIssue(Modal, title="Create GitHub Issue"):
    """Modal for GitHub issue creation."""

    title_ = TextInput[Self](label="title", placeholder="Title")
    description = TextInput[Self](
        label="Description",
        style=TextStyle.paragraph,
        placeholder="Please enter an description of the bug you are encountering.",
    )
    mcve = TextInput[Self](
        label="MCVE",
        style=TextStyle.paragraph,
        placeholder="Please provide a minimal, complete, and verifiable example of the issue.",
    )
    logs = TextInput[Self](
        label="Logs", style=TextStyle.paragraph, placeholder="Please copy and paste any relevant log output."
    )
    version = TextInput[Self](
        label="Litestar Version", placeholder="What version of Litestar are you using when encountering this issue?"
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
        issue_reporter = interaction.user
        issue_body_lines = [
            "### Reported by",
            f"[{issue_reporter.display_name}](https://discord.com/users/{issue_reporter.id}) in Discord: {interaction.channel.name}",  # noqa: E501
            "",
            "### Description",
            f"{self.description.value.strip()}",
            "",
            "### MCVE",
            f"{self.mcve.value.strip()}",
            "",
            "### Logs",
            f"{self.logs.value.strip()}",
            "",
            "### Litestar Version",
            f"{self.version.value.strip()}",
        ]
        issue_body = "\n".join(issue_body_lines)
        try:
            response_wrapper = await github_client.rest.issues.async_create(
                owner="litestar-org", repo="litestar", data={"title": self.title_.value, "body": issue_body}
            )
            if codes.is_success(response_wrapper.status_code):
                await interaction.response.send_message(
                    f"GitHub Issue created: {response_wrapper.parsed_data.html_url}", ephemeral=False
                )
            else:
                await interaction.response.send_message("Issue creation failed.", ephemeral=True)

        except Exception as e:  # noqa: BLE001
            await interaction.response.send_message(f"An error occurred: {e!s}", ephemeral=True)


class LitestarCommands(Cog):
    """Litestar command cog."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Litestar Commands"  # type: ignore[misc]
        self.context_menu = app_commands.ContextMenu(
            # TODO: Name changed to not conflict with the other one, discord shows both
            name="Create GitHub Issue",
            callback=self.create_github_issue_modal,
        )
        bot.tree.add_command(self.context_menu)

    @group(name="litestar")
    @is_byte_dev()
    async def litestar(self, ctx: Context[Bot]) -> None:
        """Commands for the Litestar guild."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid Litestar command passed...")
            await ctx.send_help(ctx.command)

    @command(
        name="apply-role-embed",
        help="Apply the role information embed to a channel.",
        aliases=["are"],
        hidden=True,
    )
    @is_owner()
    async def apply_role_embed(self, ctx: Context[Bot]) -> None:
        """Apply the role information embed to a channel.

        Args:
            ctx: Context object.
        """
        embed = Embed(title="Litestar Roles", color=0x42B1A8)

        embed.add_field(name="Organization Roles", value="\u200b", inline=False)
        embed.add_field(
            name=f"{mention_role(919261960921546815)}", value="Maintainers of the Litestar organization", inline=False
        )
        embed.add_field(
            name=f"{mention_role(1084813023044173866)}",
            value="Members invited to the Litestar organization due to their contributions",
            inline=False,
        )
        embed.add_field(
            name=f"{mention_role(1059206375814737930)}",
            value="Users that have created 3rd party libraries for Litestar projects",
            inline=False,
        )
        embed.add_field(
            name=f"{mention_role(1150487028400652339)}",
            value="Users that were once maintainers of a Litestar project or the Litestar organization",
            inline=False,
        )
        embed.add_field(
            name=f"{mention_role(919261960921546815)}",
            value=f"Programs providing services within the community. " f"(like {mention_user(1132179951567786015)}!)",
            inline=False,
        )

        embed.add_field(name="Community Roles", value="\u200b", inline=False)
        embed.add_field(
            name=f"{mention_role(1102727999285121074)}",
            value="Users that contribute financially through OpenCollective, Polar.sh, or GitHub Sponsors",
            inline=False,
        )
        embed.add_field(
            name=f"{mention_role(1150686603740729375)}",
            value="Users that help moderate the Litestar community",
            inline=False,
        )
        embed.add_field(
            name=f"{mention_role(1152668020825661570)}",
            value="Users that consistently help the members of the Litestar community",
            inline=False,
        )

        await ctx.send(embed=embed)

    async def create_github_issue_modal(self, interaction: Interaction, message: Message) -> None:
        """Context menu command to create a GitHub issue from a Discord message.

        Args:
            interaction: Interaction object.
            message: Message object.
        """
        await interaction.response.send_modal(GitHubIssue(message=message))

    @Cog.listener(name="on_message")
    async def link_github(self, message: Message):
        if message.author.bot:
            # Do not respond to bot messages
            return

        try:
            url = TypeAdapter(AnyUrl).validate_python(message.content)
        except ValidationError:
            # Not a valid URL
            return

        if url.host != "github.com":
            # Not a GitHub URL
            return

        match url.path.strip("/").split("/"):
            case (owner, repo, namespace, number):
                match cast(Literal["issues", "pull"], namespace):
                    # TODO: Add other cases and exception handling
                    case "issues":
                        issue = (await github_client.rest.issues.async_get(owner, repo, int(number))).parsed_data
                        embed = Embed(title="Summary", color=0, url=issue.html_url, description=f'[Summary]({issue.html_url})\n{issue.body}'[:4096])
                        embed.set_author(name=f"GitHub Issue: {issue.title[:242]}", url=issue.html_url)
                        from byte.lib.utils import chunk_sequence
                        from githubkit.utils import UNSET

                        # for idx, i in enumerate(chunk_sequence(f'[Summary]({issue.html_url})\n{issue.body}' or "" if issue.body is not UNSET else "", 1000)):
                            # embed.add_field(name="Summary" if not idx else "", value=''.join(i), inline=False)
                            # embed.add_field(name="", value=''.join(i), inline=False)

                        embed.add_field(name="Organization", value=owner, inline=True)
                        embed.add_field(name="Repository", value=repo, inline=True)
                        embed.add_field(name="Issue Number", value=number, inline=True)

                        embed.add_field(name="Comments", value=issue.comments)
                        embed.add_field(name="Created", value=issue.created_at, inline=False)
                        embed.add_field(name="Last Updated", value=issue.updated_at, inline=False)
                        embed.add_field(name="State", value=issue.state, inline=False)
                        embed.add_field(name="Closed at", value=issue.closed_at, inline=False)
                        embed.add_field(name="Draft", value=issue.draft, inline=False)
                        embed.add_field(name='Labels', value=','.join(label.name for label in issue.labels))
                        if issue.milestone:
                            embed.add_field(name='Milestone', value=issue.milestone.title)
                        if issue.pull_request:
                            embed.add_field(name="PR Merged At", value=issue.pull_request.merged_at, inline=False)
                            embed.add_field(name="PR HTML URL", value=issue.pull_request.html_url, inline=False)
                        issue = (await github_client.rest.issues.async_get(owner, repo, int(number))).parsed_data
                        embed.add_field(
                            name="Assignee", value=','.join(i.login for i in issue.assignees), inline=False
                        )
                        embed.add_field(name="Assignee", value=issue.assignee.login if issue.assignee else f'Unassigned - Want to try? {issue.html_url}')
                    case "pull":
                        embed = Embed(title="GitHub Pull", color=0)
                        pull = (await github_client.rest.pulls.async_get(owner, repo, int(number))).parsed_data
                        embed.add_field(name="Associated Issue", value=pull.issue_url, inline=False)
                        embed.add_field(name="PR", value=pull.html_url, inline=False)
                        embed.add_field(name="Body", value=pull.body if pull.body else "None", inline=False)
                        embed.add_field(name="Created at", value=pull.created_at, inline=False)

                await message.channel.send(embed=embed)
            case _:
                # Invalid GitHub URL
                return


async def setup(bot: Bot) -> None:
    """Add cog to bot.

    Args:
        bot: Bot object.
    """
    await bot.add_cog(LitestarCommands(bot))
    # TODO: Only sync the appropriate guilds needed.
    #    This is a temporary fix to get the context menu working.
    #    The invite link was generated with correct permissions, but it seems that it still won't work?
    #    cc: @alc-alc
    #    ExtensionFailed: Extension 'src.byte.plugins.custom.litestar' raised an error: Forbidden: 403 Forbidden (error code: 50001): Missing Access  # noqa: E501
    #
    # cog = LitestarCommands(bot)
    # await bot.add_cog(cog)
    # await bot.tree.sync(guild=Object(id=919193495116337154))
    # await bot.tree.sync(guild=Object(id=discord.DEV_GUILD_ID))
