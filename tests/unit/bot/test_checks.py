"""Tests for permission check decorators."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from discord.ext.commands import CheckFailure

from byte_bot.lib.checks import is_byte_dev, is_guild_admin

if TYPE_CHECKING:
    from discord.ext.commands import Context


class TestIsGuildAdmin:
    """Tests for is_guild_admin check."""

    @pytest.fixture
    def admin_context(self, mock_context: Context) -> Context:
        """Create context with admin member."""
        mock_member = MagicMock()
        mock_member.guild_permissions.administrator = True
        mock_context.guild.get_member = MagicMock(return_value=mock_member)
        mock_context.author.id = 987654321
        return mock_context

    @pytest.fixture
    def non_admin_context(self, mock_context: Context) -> Context:
        """Create context with non-admin member."""
        mock_member = MagicMock()
        mock_member.guild_permissions.administrator = False
        mock_context.guild.get_member = MagicMock(return_value=mock_member)
        mock_context.author.id = 987654321
        return mock_context

    @pytest.fixture
    def dm_context(self, mock_context: Context) -> Context:
        """Create context without guild (DM)."""
        mock_context.guild = None
        return mock_context

    async def test_guild_admin_check_passes_for_admin(self, admin_context: Context) -> None:
        """Test is_guild_admin allows guild administrators."""
        check = is_guild_admin()

        # The check returns a check function, we need to call it
        result = await check.predicate(admin_context)

        assert result is True

    async def test_guild_admin_check_fails_for_non_admin(self, non_admin_context: Context) -> None:
        """Test is_guild_admin denies non-administrators."""
        check = is_guild_admin()

        result = await check.predicate(non_admin_context)

        assert result is False

    async def test_guild_admin_check_raises_in_dm(self, dm_context: Context) -> None:
        """Test is_guild_admin raises CheckFailure in DMs."""
        check = is_guild_admin()

        with pytest.raises(CheckFailure) as exc_info:
            await check.predicate(dm_context)

        assert "guild" in str(exc_info.value).lower()

    async def test_guild_admin_check_raises_when_member_not_found(self, mock_context: Context) -> None:
        """Test is_guild_admin raises CheckFailure when member not in guild."""
        mock_context.guild.get_member = MagicMock(return_value=None)
        check = is_guild_admin()

        with pytest.raises(CheckFailure) as exc_info:
            await check.predicate(mock_context)

        assert "Member not found" in str(exc_info.value)

    async def test_guild_admin_check_verifies_correct_member(self, admin_context: Context) -> None:
        """Test is_guild_admin checks the correct member ID."""
        check = is_guild_admin()

        await check.predicate(admin_context)

        admin_context.guild.get_member.assert_called_once_with(admin_context.author.id)


class TestIsByteDev:
    """Tests for is_byte_dev check."""

    @pytest.fixture
    def owner_context(self, mock_context: Context) -> Context:
        """Create context where author is bot owner."""
        mock_context.bot.is_owner = AsyncMock(return_value=True)
        return mock_context

    @pytest.fixture
    def dev_user_context(self, mock_context: Context) -> Context:
        """Create context where author is configured dev user."""
        mock_context.bot.is_owner = AsyncMock(return_value=False)
        mock_context.author.id = 999999999  # Will be configured as dev user
        return mock_context

    @pytest.fixture
    def byte_dev_role_context(self, mock_context: Context) -> Context:
        """Create context where author has byte-dev role."""
        mock_context.bot.is_owner = AsyncMock(return_value=False)
        mock_context.author.id = 111111111  # Different from dev user

        # Create member with byte-dev role
        mock_member = MagicMock()
        byte_dev_role = MagicMock()
        byte_dev_role.name = "byte-dev"
        mock_member.roles = [byte_dev_role]
        mock_context.guild.get_member = MagicMock(return_value=mock_member)

        return mock_context

    @pytest.fixture
    def regular_user_context(self, mock_context: Context) -> Context:
        """Create context with regular user (no special permissions)."""
        mock_context.bot.is_owner = AsyncMock(return_value=False)
        mock_context.author.id = 111111111

        # Create member without byte-dev role
        mock_member = MagicMock()
        regular_role = MagicMock()
        regular_role.name = "member"
        mock_member.roles = [regular_role]
        mock_context.guild.get_member = MagicMock(return_value=mock_member)

        return mock_context

    @pytest.fixture
    def dm_regular_user_context(self, mock_context: Context) -> Context:
        """Create DM context with regular user."""
        mock_context.bot.is_owner = AsyncMock(return_value=False)
        mock_context.author.id = 111111111
        mock_context.guild = None
        return mock_context

    async def test_byte_dev_check_passes_for_owner(self, owner_context: Context) -> None:
        """Test is_byte_dev allows bot owner."""
        check = is_byte_dev()

        with patch("byte_bot.lib.checks.bot_settings") as mock_settings:
            mock_settings.discord_dev_user_id = 999999999
            result = await check.predicate(owner_context)

        assert result is True

    async def test_byte_dev_check_passes_for_dev_user(self, dev_user_context: Context) -> None:
        """Test is_byte_dev allows configured dev user."""
        check = is_byte_dev()

        with patch("byte_bot.lib.checks.bot_settings") as mock_settings:
            mock_settings.discord_dev_user_id = 999999999
            result = await check.predicate(dev_user_context)

        assert result is True

    async def test_byte_dev_check_passes_for_byte_dev_role(self, byte_dev_role_context: Context) -> None:
        """Test is_byte_dev allows users with byte-dev role."""
        check = is_byte_dev()

        with patch("byte_bot.lib.checks.bot_settings") as mock_settings:
            mock_settings.discord_dev_user_id = 999999999
            result = await check.predicate(byte_dev_role_context)

        assert result is True

    async def test_byte_dev_check_fails_for_regular_user(self, regular_user_context: Context) -> None:
        """Test is_byte_dev denies regular users."""
        check = is_byte_dev()

        with patch("byte_bot.lib.checks.bot_settings") as mock_settings:
            mock_settings.discord_dev_user_id = 999999999
            result = await check.predicate(regular_user_context)

        assert result is False

    async def test_byte_dev_check_fails_in_dm_for_regular_user(self, dm_regular_user_context: Context) -> None:
        """Test is_byte_dev denies regular users in DMs."""
        check = is_byte_dev()

        with patch("byte_bot.lib.checks.bot_settings") as mock_settings:
            mock_settings.discord_dev_user_id = 999999999
            result = await check.predicate(dm_regular_user_context)

        assert result is False

    async def test_byte_dev_check_fails_when_member_not_found(self, mock_context: Context) -> None:
        """Test is_byte_dev denies when member not in guild."""
        mock_context.bot.is_owner = AsyncMock(return_value=False)
        mock_context.author.id = 111111111
        mock_context.guild.get_member = MagicMock(return_value=None)
        check = is_byte_dev()

        with patch("byte_bot.lib.checks.bot_settings") as mock_settings:
            mock_settings.discord_dev_user_id = 999999999
            result = await check.predicate(mock_context)

        assert result is False

    async def test_byte_dev_check_owner_in_dm(self, mock_context: Context) -> None:
        """Test is_byte_dev allows owner even in DMs."""
        mock_context.bot.is_owner = AsyncMock(return_value=True)
        mock_context.guild = None
        check = is_byte_dev()

        with patch("byte_bot.lib.checks.bot_settings") as mock_settings:
            mock_settings.discord_dev_user_id = 999999999
            result = await check.predicate(mock_context)

        assert result is True

    async def test_byte_dev_check_multiple_roles(self, mock_context: Context) -> None:
        """Test is_byte_dev finds byte-dev role among multiple roles."""
        mock_context.bot.is_owner = AsyncMock(return_value=False)
        mock_context.author.id = 111111111

        # Create member with multiple roles
        mock_member = MagicMock()
        role1 = MagicMock()
        role1.name = "member"
        role2 = MagicMock()
        role2.name = "byte-dev"
        role3 = MagicMock()
        role3.name = "moderator"
        mock_member.roles = [role1, role2, role3]
        mock_context.guild.get_member = MagicMock(return_value=mock_member)

        check = is_byte_dev()

        with patch("byte_bot.lib.checks.bot_settings") as mock_settings:
            mock_settings.discord_dev_user_id = 999999999
            result = await check.predicate(mock_context)

        assert result is True

    async def test_byte_dev_check_case_sensitive_role_name(self, mock_context: Context) -> None:
        """Test is_byte_dev role name is case-sensitive."""
        mock_context.bot.is_owner = AsyncMock(return_value=False)
        mock_context.author.id = 111111111

        # Create member with wrong case role
        mock_member = MagicMock()
        role = MagicMock()
        role.name = "Byte-Dev"  # Wrong case
        mock_member.roles = [role]
        mock_context.guild.get_member = MagicMock(return_value=mock_member)

        check = is_byte_dev()

        with patch("byte_bot.lib.checks.bot_settings") as mock_settings:
            mock_settings.discord_dev_user_id = 999999999
            result = await check.predicate(mock_context)

        assert result is False

    async def test_byte_dev_check_calls_is_owner(self, mock_context: Context) -> None:
        """Test is_byte_dev calls bot.is_owner with correct author."""
        mock_context.bot.is_owner = AsyncMock(return_value=False)
        mock_context.guild = None
        check = is_byte_dev()

        with patch("byte_bot.lib.checks.bot_settings") as mock_settings:
            mock_settings.discord_dev_user_id = 999999999
            await check.predicate(mock_context)

        mock_context.bot.is_owner.assert_called_once_with(mock_context.author)
