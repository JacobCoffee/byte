"""Plugins for events."""
import discord
from discord.ext.commands import Bot, Cog

__all__ = ("Events", "setup")


class Events(Cog):
    """Events cog."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot

    @Cog.listener()
    async def on_thread_create(self, thread: discord.Thread) -> None:
        """Handle thread create event.

        .. todo:: parameterize the command prefix per guild, and the
            mention tag per guild.

        Args:
            thread (discord.Thread): Thread that was created.
        """
        if thread.parent.name == "help":
            reply = (
                f"At your assistance, {thread.owner.mention}.\n"
                f"Make sure you include an [MCVE](https://stackoverflow.com/help/minimal-reproducible-example) in "
                f"your post if relevant.\n"
                f"When you are done you can tag your post as ***✅ Solved*** or type `!solve`!\n"
                f"If no one responds within a reasonable amount of time, please ping `@Member`."
            )
            await thread.send(reply)
        elif thread.parent.name == "forum":
            reply = f"Thanks for posting, {thread.owner.mention}!"
            await thread.send(reply)


async def setup(bot: Bot) -> None:
    """Set up the Events cog."""
    await bot.add_cog(Events(bot))
