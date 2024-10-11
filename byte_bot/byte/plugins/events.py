"""Plugins for events."""

from threading import Thread
from typing import cast

from discord import Embed
from discord.ext.commands import Bot, Cog

from byte_bot.byte.lib.common.assets import litestar_logo_yellow
from byte_bot.byte.lib.common.links import mcve
from byte_bot.byte.lib.utils import linker
from byte_bot.byte.views.forums import HelpThreadView

__all__ = ("Events", "setup")


class Events(Cog):
    """Events cog."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot

    @Cog.listener()
    async def on_thread_create(self, thread: Thread) -> None:
        """Handle thread create event.

        .. todo:: parameterize the command prefix per guild, and the
            mention tag per guild.

        Args:
            thread (discord.Thread): Thread that was created.
        """
        if thread.parent.name == "help":
            embed = Embed(title=f"Notes for {thread.name}", color=0x42B1A8)
            embed.add_field(name="At your assistance", value=f"{thread.owner.mention}", inline=False)
            embed.add_field(
                name="No Response?", value="If no response in a reasonable time, ping @Member.", inline=True
            )
            commands_to_solve = " or ".join(
                f"`{command_prefix}solve`" for command_prefix in cast(list[str], self.bot.command_prefix)
            )
            embed.add_field(name="Closing", value=f"To close, type {commands_to_solve}.", inline=True)
            embed.add_field(
                name="MCVE",
                value=f"Please include an {linker('MCVE', mcve)} so that we can reproduce your issue locally.",
                inline=False,
            )
            embed.set_thumbnail(url=litestar_logo_yellow)
            view = HelpThreadView(author=thread.owner, guild_id=thread.guild.id, bot=self.bot)
            await view.setup()
            await thread.send(embed=embed, view=view)
        elif thread.parent.name == "forum":
            reply = f"Thanks for posting, {thread.owner.mention}!"
            await thread.send(reply)


async def setup(bot: Bot) -> None:
    """Set up the Events cog."""
    await bot.add_cog(Events(bot))
