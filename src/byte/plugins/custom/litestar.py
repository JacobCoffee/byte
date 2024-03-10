"""Custom plugins for the Litestar Discord."""
from __future__ import annotations

import datetime

from dateutil.zoneinfo import gettz
from discord import Embed, EntityType, Interaction, Object, PrivacyLevel
from discord.app_commands import command as app_command
from discord.ext.commands import Bot, Cog, Context, command, group, is_owner

from byte.lib.common.colors import litestar_yellow
from byte.lib.utils import get_next_friday, is_byte_dev, mention_role, mention_user

__all__ = ("LitestarCommands", "setup")


class LitestarCommands(Cog):
    """Litestar command cog."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Litestar Commands"  # type: ignore[misc]

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
        embed = Embed(title="Litestar Roles", color=litestar_yellow)

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

    @app_command(
        name="schedule-office-hours",
        description="Schedule Office Hours event for the upcoming or the week after next Friday.",
    )
    async def schedule_office_hours(self, interaction: Interaction, delay: int | None = None) -> None:
        """Schedule Office Hours event for the upcoming or ``delay`` weeks after next Friday.

        Args:
            interaction: Interaction object.
            delay: Optional. Number of weeks to delay the event.
        """
        now_cst = datetime.datetime.now(gettz("America/Chicago"))
        start_dt, end_dt = get_next_friday(now_cst, delay)
        existing_events = interaction.guild.scheduled_events

        for event in existing_events:
            if (
                event.name == "Office Hours"
                and event.start_time.astimezone(gettz("America/Chicago")).date() == start_dt.date()
            ):
                await interaction.response.send_message(
                    "An Office Hours event is already scheduled for that day.", ephemeral=True
                )
                return

        await interaction.guild.create_scheduled_event(
            name="Office Hours",
            start_time=start_dt,
            end_time=end_dt,
            description="Join us for our weekly office hours!",
            entity_type=EntityType.stage_instance,
            privacy_level=PrivacyLevel.guild_only,
            reason=f"Scheduled by {interaction.user} via /schedule-office-hours",
            channel=Object(id=1215926860144443502),
        )

        formatted_date = f"<t:{int(start_dt.timestamp())}:D>"
        start_time_formatted = f"<t:{int(start_dt.timestamp())}:t>"
        end_time_formatted = f"<t:{int(end_dt.timestamp())}:t>"

        await interaction.response.send_message(
            f"Office Hours event scheduled: {formatted_date} from {start_time_formatted} - {end_time_formatted}."
        )


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
