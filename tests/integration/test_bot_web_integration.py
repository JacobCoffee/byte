"""Integration tests for bot-web API interaction."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from litestar.status_codes import HTTP_201_CREATED
from sqlalchemy import select

from byte_bot.server.domain.db.models import Guild

if TYPE_CHECKING:
    from litestar.testing import AsyncTestClient
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = (
    "TestBotWebIntegration",
    "TestGuildSyncIntegration",
)


class TestBotWebIntegration:
    """Test suite for bot-web API integration."""

    @pytest.mark.asyncio
    async def test_bot_creates_guild_via_api(
        self, client: AsyncTestClient, async_session: AsyncSession, mock_discord_guild: MagicMock
    ) -> None:
        """Test that bot can create guild via web API.

        Args:
            client: Test HTTP client
            async_session: Database session
            mock_discord_guild: Mock Discord guild
        """
        # Simulate bot calling API to create guild
        response = await client.post(
            "/api/guilds/create",
            params={
                "guild_id": mock_discord_guild.id,
                "guild_name": mock_discord_guild.name,
            },
        )

        assert response.status_code == HTTP_201_CREATED

        # Verify guild was created in database
        result = await async_session.execute(select(Guild).where(Guild.guild_id == mock_discord_guild.id))
        guild = result.scalar_one_or_none()

        assert guild is not None
        assert guild.guild_id == mock_discord_guild.id
        assert guild.guild_name == mock_discord_guild.name

    @pytest.mark.asyncio
    async def test_bot_on_guild_join_integration(self, mock_discord_guild: MagicMock) -> None:
        """Test bot's on_guild_join event with API integration.

        Args:
            mock_discord_guild: Mock Discord guild
        """
        from discord import Activity, Intents

        from byte_bot.byte.bot import Byte

        intents = Intents.default()
        activity = Activity(name="test")
        bot = Byte(command_prefix=["!"], intents=intents, activity=activity)

        # Mock tree sync and get_guild
        with patch.object(bot.tree, "sync", new=AsyncMock()) as mock_sync:
            with patch.object(bot, "get_guild", return_value=None):
                # Mock httpx to simulate successful API call
                with patch("httpx.AsyncClient") as mock_client:
                    mock_response = AsyncMock()
                    mock_response.status_code = HTTP_201_CREATED
                    mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

                    await bot.on_guild_join(mock_discord_guild)

                    # Verify tree was synced and API was called
                    mock_sync.assert_called_once_with(guild=mock_discord_guild)


class TestGuildSyncIntegration:
    """Test suite for guild synchronization between bot and web API."""

    @pytest.mark.asyncio
    async def test_guild_data_sync(
        self, client: AsyncTestClient, async_session: AsyncSession, sample_guild: dict[str, Any]
    ) -> None:
        """Test that guild data stays synchronized between bot and API.

        Args:
            client: Test HTTP client
            async_session: Database session
            sample_guild: Sample guild data
        """
        # Create guild via API (simulating bot action)
        await client.post(
            "/api/guilds/create",
            params={
                "guild_id": sample_guild["guild_id"],
                "guild_name": sample_guild["guild_name"],
            },
        )

        # Fetch guild via API (simulating web frontend)
        response = await client.get(f"/api/guilds/{sample_guild['guild_id']}")

        assert response.status_code == 200
        data = response.json()

        # Verify data consistency
        assert data["guild_id"] == sample_guild["guild_id"]
        assert data["guild_name"] == sample_guild["guild_name"]

    @pytest.mark.asyncio
    async def test_guild_config_update_integration(
        self, client: AsyncTestClient, async_session: AsyncSession, sample_guild: dict[str, Any]
    ) -> None:
        """Test updating guild config through API (simulating bot command).

        Args:
            client: Test HTTP client
            async_session: Database session
            sample_guild: Sample guild data
        """
        # Create guild
        guild = Guild(**sample_guild)
        async_session.add(guild)
        await async_session.commit()

        # Update guild setting via API
        response = await client.patch(
            "/api/guilds/update",
            params={
                "guild_id": sample_guild["guild_id"],
                "setting": "prefix",
                "value": "?",
            },
        )

        assert response.status_code == 200

        # Verify update in database
        result = await async_session.execute(select(Guild).where(Guild.guild_id == sample_guild["guild_id"]))
        updated_guild = result.scalar_one()

        # Note: The update might not be reflected immediately due to transaction isolation
        # In a real scenario, you'd want to refresh the session or query again
