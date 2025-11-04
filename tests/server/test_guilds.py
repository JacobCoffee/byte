"""Tests for guild management (controllers, services, and models)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from httpx import AsyncClient
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from byte_bot.server.domain.db.models import Guild, GitHubConfig, SOTagsConfig

if TYPE_CHECKING:
    from litestar.testing import AsyncTestClient

__all__ = (
    "TestGuildController",
    "TestGuildModels",
)


@pytest.mark.skip(reason="Requires full app setup with test database")
class TestGuildController:
    """Test suite for Guild API endpoints."""

    @pytest.mark.asyncio
    async def test_create_guild(self, client: AsyncTestClient, sample_guild: dict[str, Any]) -> None:
        """Test creating a guild via API.

        Args:
            client: Test HTTP client
            sample_guild: Sample guild data
        """
        response = await client.post(
            "/api/guilds/create",
            params={
                "guild_id": sample_guild["guild_id"],
                "guild_name": sample_guild["guild_name"],
            },
        )

        assert response.status_code == HTTP_201_CREATED
        assert "created" in response.text.lower()

    @pytest.mark.asyncio
    async def test_list_guilds_empty(self, client: AsyncTestClient) -> None:
        """Test listing guilds when database is empty.

        Args:
            client: Test HTTP client
        """
        response = await client.get("/api/guilds")

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_list_guilds_with_data(
        self, client: AsyncTestClient, async_session: AsyncSession, sample_guild: dict[str, Any]
    ) -> None:
        """Test listing guilds with data.

        Args:
            client: Test HTTP client
            async_session: Database session
            sample_guild: Sample guild data
        """
        # Create a guild in the database
        guild = Guild(**sample_guild)
        async_session.add(guild)
        await async_session.commit()

        response = await client.get("/api/guilds")

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0

    @pytest.mark.asyncio
    async def test_get_guild_detail(
        self, client: AsyncTestClient, async_session: AsyncSession, sample_guild: dict[str, Any]
    ) -> None:
        """Test getting guild details by ID.

        Args:
            client: Test HTTP client
            async_session: Database session
            sample_guild: Sample guild data
        """
        # Create a guild in the database
        guild = Guild(**sample_guild)
        async_session.add(guild)
        await async_session.commit()

        response = await client.get(f"/api/guilds/{sample_guild['guild_id']}")

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["guild_id"] == sample_guild["guild_id"]
        assert data["guild_name"] == sample_guild["guild_name"]

    @pytest.mark.asyncio
    async def test_get_guild_not_found(self, client: AsyncTestClient) -> None:
        """Test getting a non-existent guild.

        Args:
            client: Test HTTP client
        """
        response = await client.get("/api/guilds/999999999")

        assert response.status_code == HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_guild_setting(
        self, client: AsyncTestClient, async_session: AsyncSession, sample_guild: dict[str, Any]
    ) -> None:
        """Test updating a guild setting.

        Args:
            client: Test HTTP client
            async_session: Database session
            sample_guild: Sample guild data
        """
        # Create a guild in the database
        guild = Guild(**sample_guild)
        async_session.add(guild)
        await async_session.commit()

        # Update the prefix
        response = await client.patch(
            "/api/guilds/update",
            params={
                "guild_id": sample_guild["guild_id"],
                "setting": "prefix",
                "value": "?",
            },
        )

        assert response.status_code == HTTP_200_OK


class TestGuildModels:
    """Test suite for Guild database models."""

    @pytest.mark.asyncio
    async def test_create_guild_model(self, async_session: AsyncSession, sample_guild: dict[str, Any]) -> None:
        """Test creating a Guild model.

        Args:
            async_session: Database session
            sample_guild: Sample guild data
        """
        guild = Guild(**sample_guild)
        async_session.add(guild)
        await async_session.commit()

        # Verify the guild was created
        result = await async_session.execute(select(Guild).where(Guild.guild_id == sample_guild["guild_id"]))
        saved_guild = result.scalar_one()

        assert saved_guild.guild_name == sample_guild["guild_name"]
        assert saved_guild.prefix == sample_guild["prefix"]

    @pytest.mark.asyncio
    async def test_guild_with_github_config(
        self,
        async_session: AsyncSession,
        sample_guild: dict[str, Any],
        sample_github_config: dict[str, Any],
    ) -> None:
        """Test Guild with associated GitHub config.

        Args:
            async_session: Database session
            sample_guild: Sample guild data
            sample_github_config: Sample GitHub config data
        """
        # Create guild
        guild = Guild(**sample_guild)
        async_session.add(guild)
        await async_session.flush()

        # Create GitHub config
        github_config = GitHubConfig(**sample_github_config)
        async_session.add(github_config)
        await async_session.commit()

        # Verify relationship
        result = await async_session.execute(
            select(GitHubConfig).where(GitHubConfig.guild_id == sample_guild["guild_id"])
        )
        saved_config = result.scalar_one()

        assert saved_config.github_organization == sample_github_config["github_organization"]
        assert saved_config.github_repository == sample_github_config["github_repository"]

    @pytest.mark.asyncio
    async def test_guild_with_sotags(
        self,
        async_session: AsyncSession,
        sample_guild: dict[str, Any],
        sample_sotags_config: dict[str, Any],
    ) -> None:
        """Test Guild with Stack Overflow tags config.

        Args:
            async_session: Database session
            sample_guild: Sample guild data
            sample_sotags_config: Sample SO tags config data
        """
        # Create guild
        guild = Guild(**sample_guild)
        async_session.add(guild)
        await async_session.flush()

        # Create SO tags config
        sotags = SOTagsConfig(**sample_sotags_config)
        async_session.add(sotags)
        await async_session.commit()

        # Verify
        result = await async_session.execute(
            select(SOTagsConfig).where(SOTagsConfig.guild_id == sample_guild["guild_id"])
        )
        saved_config = result.scalar_one()

        assert saved_config.tag_name == sample_sotags_config["tag_name"]

    @pytest.mark.asyncio
    async def test_guild_unique_constraint(self, async_session: AsyncSession, sample_guild: dict[str, Any]) -> None:
        """Test guild_id unique constraint.

        Args:
            async_session: Database session
            sample_guild: Sample guild data
        """
        # Create first guild
        guild1 = Guild(**sample_guild)
        async_session.add(guild1)
        await async_session.commit()

        # Try to create duplicate guild (same guild_id)
        guild2 = Guild(**sample_guild)
        async_session.add(guild2)

        with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_guild_default_values(self, async_session: AsyncSession) -> None:
        """Test Guild model default values.

        Args:
            async_session: Database session
        """
        guild = Guild(guild_id=123456, guild_name="Test Guild")
        async_session.add(guild)
        await async_session.commit()

        result = await async_session.execute(select(Guild).where(Guild.guild_id == 123456))
        saved_guild = result.scalar_one()

        assert saved_guild.prefix == "!"
        assert saved_guild.issue_linking is False
        assert saved_guild.comment_linking is False
        assert saved_guild.pep_linking is False
