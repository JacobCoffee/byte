"""Custom plugins for the Litestar Discord."""
from __future__ import annotations

from discord import Embed, Interaction, Message, app_commands
from discord.ext.commands import Bot, Cog, Context, command, group, is_owner

from src.byte.lib.utils import is_byte_dev, mention_role, mention_user
from src.server.domain.github.helpers import github_client

__all__ = ("LitestarCommands", "setup")


class LitestarCommands(Cog):
    """Litestar command cog."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Litestar Commands"  # type: ignore[misc]
        self.context_menu = app_commands.ContextMenu(name="Create GitHub Issue", callback=self.create_github_issue)
        bot.tree.add_command(self.context_menu)

    @group(name="litestar")
    @is_byte_dev()
    async def litestar(self, ctx: Context) -> None:
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
    async def apply_role_embed(self, ctx: Context) -> None:
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

    async def create_github_issue(self, interaction: Interaction, message: Message) -> None:
        """Context menu command to create a GitHub issue from a Discord message.

        Args:
            interaction: Interaction object.
            message: Message object.
        """
        issue_title = "Issue from Discord"
        issue_reporter = message.author
        issue_body = (
            f"Reported by {issue_reporter.display_name} in Discord: {message.channel.mention}:\n\n{message.content}"
        )

        try:
            response_wrapper = await github_client.rest.issues.async_create(
                owner="litestar-org", repo="litestar", data={"title": issue_title, "body": issue_body}
            )

            if response_wrapper._response.is_success:
                issue_data = response_wrapper._data_model.parse_obj(response_wrapper._response.json())
                issue_url = issue_data.html_url
                await interaction.response.send_message(f"GitHub Issue created: {issue_url}", ephemeral=False)
            else:
                await interaction.response.send_message("Issue creation failed.", ephemeral=True)

        except Exception as e:  # noqa: BLE001
            await interaction.response.send_message(f"An error occurred: {e!s}", ephemeral=True)


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
