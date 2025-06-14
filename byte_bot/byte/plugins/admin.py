"""Plugins for admins.

.. todo:: add an unload cog command.
"""

import discord
import httpx
from discord import Interaction
from discord.app_commands import command as app_command
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context, command, group, is_owner
from httpx import ConnectError

__all__ = ("AdminCommands", "setup")

from byte_bot.byte.lib.checks import is_byte_dev
from byte_bot.byte.lib import settings
from byte_bot.byte.lib.log import get_logger
from byte_bot.server.lib.settings import ServerSettings

logger = get_logger()
server_settings = ServerSettings()


class AdminCommands(Cog):
    """Admin command cog."""

    def __init__(self, bot: Bot) -> None:
        """Initialize cog."""
        self.bot = bot
        self.__cog_name__ = "Admin Commands"  # type: ignore[misc]

    @group(name="admin")
    @is_byte_dev()
    async def admin(self, ctx: Context) -> None:
        """Commands for bot admins."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid admin command passed...")
            await ctx.send_help(ctx.command)

    @command(name="list-cogs", help="Lists all loaded cogs.", aliases=["lc"], hidden=True)
    @is_owner()
    async def list_cogs(self, ctx: Context) -> None:
        """Lists all loaded cogs.

        Args:
            ctx: Context object.
        """
        cogs = [cog.split(".")[-1] for cog in self.bot.extensions]
        await ctx.send(f"Loaded cogs: {', '.join(cogs)}")

    @command(name="reload", help="Reloads a cog.", aliases=["rl"], hidden=True)
    @is_owner()
    async def reload(self, ctx: Context, cog: str = "all") -> None:
        """Reloads a cog or all cogs if specified.

        Args:
            ctx: Context object.
            cog: Name of cog to reload. Default is "all".
        """
        if cog.lower() == "all":
            await self.reload_all_cogs(ctx)
        else:
            await self.reload_single_cog(ctx, cog)

    async def reload_all_cogs(self, ctx: Context) -> None:
        """Reload all cogs.

        Args:
            ctx: Context object.
        """
        results = []
        for extension in list(self.bot.extensions):
            cog_name = extension.split(".")[-1]
            result = await self.reload_single_cog(ctx, cog_name, send_message=False)
            results.append(result)
        results.append("All cogs reloaded!")
        await ctx.send("\n".join(results))

    async def reload_single_cog(self, ctx: Context, cog: str, send_message: bool = True) -> str:
        """Reload a single cog."""
        try:
            await self.bot.reload_extension(f"plugins.{cog}")
            message = f"Cog `{cog}` reloaded!"
        except (commands.ExtensionNotLoaded, commands.ExtensionNotFound) as e:
            message = f"Error with cog `{cog}`: {e!s}"

        if send_message:
            await ctx.send(message)

        return message

    @app_command(name="sync")
    @is_byte_dev()
    async def tree_sync(self, interaction: Interaction) -> None:
        """Slash command to perform a global sync."""
        results = await self.bot.tree.sync()
        await interaction.response.send_message("\n".join(i.name for i in results), ephemeral=True)

    @command(name="bootstrap-guild", help="Bootstrap existing guild to database (dev only).", hidden=True)
    @is_byte_dev()
    async def bootstrap_guild(self, ctx: Context, guild_id: int | None = None) -> None:
        """Bootstrap an existing guild to the database.
        
        Args:
            ctx: Context object.
            guild_id: Guild ID to bootstrap. If not provided, uses current guild.
        """
        guild = await self._get_target_guild(ctx, guild_id)
        if not guild:
            return
            
        await ctx.send(f"🔄 Bootstrapping guild {guild.name} (ID: {guild.id})...")
        
        await self._sync_guild_commands(guild)
        await self._register_guild_in_database(ctx, guild)

    async def _get_target_guild(self, ctx: Context, guild_id: int | None) -> discord.Guild | None:
        """Get the target guild for bootstrapping."""
        target_guild_id = guild_id or (ctx.guild.id if ctx.guild else None)
        
        if not target_guild_id:
            await ctx.send("❌ No guild ID provided and command not used in a guild.")
            return None
            
        guild = self.bot.get_guild(target_guild_id)
        if not guild:
            await ctx.send(f"❌ Bot is not in guild with ID {target_guild_id}")
            return None
            
        return guild

    async def _sync_guild_commands(self, guild: discord.Guild) -> None:
        """Sync commands to the guild."""
        try:
            await self.bot.tree.sync(guild=guild)
            logger.info("Commands synced to guild %s (id: %s)", guild.name, guild.id)
        except Exception as e:
            logger.error("Failed to sync commands to guild %s: %s", guild.name, e)

    async def _register_guild_in_database(self, ctx: Context, guild: discord.Guild) -> None:
        """Register guild in database via API."""
        api_url = f"http://{server_settings.HOST}:{server_settings.PORT}/api/guilds/create?guild_id={guild.id}&guild_name={guild.name}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(api_url)
                await self._handle_api_response(ctx, guild, response)
        except ConnectError:
            error_msg = f"Failed to connect to API to bootstrap guild {guild.name} (id: {guild.id})"
            logger.exception(error_msg)
            await ctx.send(f"❌ {error_msg}")

    async def _handle_api_response(self, ctx: Context, guild: discord.Guild, response: httpx.Response) -> None:
        """Handle API response for guild registration."""
        if response.status_code == httpx.codes.CREATED:
            await self._send_success_message(ctx, guild)
            await self._notify_dev_channel(guild)
        elif response.status_code == httpx.codes.CONFLICT:
            await ctx.send(f"⚠️ Guild {guild.name} already exists in database")
        else:
            error_msg = f"Failed to add guild to database (status: {response.status_code})"
            logger.error(error_msg)
            await ctx.send(f"❌ {error_msg}")

    async def _send_success_message(self, ctx: Context, guild: discord.Guild) -> None:
        """Send success message to user."""
        logger.info("Successfully bootstrapped guild %s (id: %s)", guild.name, guild.id)
        embed = discord.Embed(
            title="Guild Bootstrapped",
            description=f"Successfully bootstrapped guild {guild.name} (ID: {guild.id})",
            color=discord.Color.green(),
        )
        embed.add_field(name="Commands Synced", value="✅", inline=True)
        embed.add_field(name="Database Entry", value="✅", inline=True)
        await ctx.send(embed=embed)

    async def _notify_dev_channel(self, guild: discord.Guild) -> None:
        """Notify dev channel about guild bootstrap."""
        dev_guild = self.bot.get_guild(settings.discord.DEV_GUILD_ID)
        if not dev_guild:
            return
            
        dev_channel = dev_guild.get_channel(settings.discord.DEV_GUILD_INTERNAL_ID)
        if not dev_channel or not hasattr(dev_channel, "send"):
            return
            
        embed = discord.Embed(
            title="Guild Bootstrapped",
            description=f"Guild {guild.name} (ID: {guild.id}) was manually bootstrapped",
            color=discord.Color.blue(),
        )
        await dev_channel.send(embed=embed)  # type: ignore[attr-defined]


async def setup(bot: Bot) -> None:
    """Add cog to bot.

    Args:
        bot: Bot object.
    """
    await bot.add_cog(AdminCommands(bot))
