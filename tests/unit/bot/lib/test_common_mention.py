"""Tests for lib/common/mention.py utility functions."""

from __future__ import annotations

from byte_bot.lib.common.mention import (
    mention_channel,
    mention_custom_emoji,
    mention_custom_emoji_animated,
    mention_guild_navigation,
    mention_role,
    mention_slash_command,
    mention_timestamp,
    mention_user,
    mention_user_nickname,
)


def test_mention_user() -> None:
    """Test mention_user formats user ID."""
    assert mention_user(123456789) == "<@123456789>"
    assert mention_user(987654321) == "<@987654321>"


def test_mention_user_nickname() -> None:
    """Test mention_user_nickname formats user ID with nickname format."""
    assert mention_user_nickname(123456789) == "<@!123456789>"
    assert mention_user_nickname(987654321) == "<@!987654321>"


def test_mention_channel() -> None:
    """Test mention_channel formats channel ID."""
    assert mention_channel(111222333) == "<#111222333>"
    assert mention_channel(444555666) == "<#444555666>"


def test_mention_role() -> None:
    """Test mention_role formats role ID."""
    assert mention_role(777888999) == "<@&777888999>"
    assert mention_role(123123123) == "<@&123123123>"


def test_mention_slash_command() -> None:
    """Test mention_slash_command formats command."""
    assert mention_slash_command("help", 111) == "</help:111>"
    assert mention_slash_command("ping", 222) == "</ping:222>"
    assert mention_slash_command("config", 333) == "</config:333>"


def test_mention_timestamp_without_style() -> None:
    """Test mention_timestamp formats Unix timestamp without style."""
    assert mention_timestamp(1234567890) == "<t:1234567890>"
    assert mention_timestamp(9876543210) == "<t:9876543210>"
    assert mention_timestamp(0) == "<t:0>"


def test_mention_timestamp_with_style() -> None:
    """Test mention_timestamp formats Unix timestamp with style."""
    assert mention_timestamp(1234567890, "R") == "<t:1234567890:R>"
    assert mention_timestamp(9876543210, "F") == "<t:9876543210:F>"
    assert mention_timestamp(0, "t") == "<t:0:t>"


def test_mention_custom_emoji() -> None:
    """Test mention_custom_emoji formats custom emoji."""
    assert mention_custom_emoji("smile", 123) == "<:smile:123>"
    assert mention_custom_emoji("fire", 456) == "<:fire:456>"
    assert mention_custom_emoji("tada", 789) == "<:tada:789>"


def test_mention_custom_emoji_animated() -> None:
    """Test mention_custom_emoji_animated formats animated emoji."""
    assert mention_custom_emoji_animated("smile", 123) == "<a:smile:123>"
    assert mention_custom_emoji_animated("fire", 456) == "<a:fire:456>"
    assert mention_custom_emoji_animated("tada", 789) == "<a:tada:789>"


def test_mention_guild_navigation() -> None:
    """Test mention_guild_navigation formats guild navigation elements."""
    assert mention_guild_navigation("customize", 111) == "<111:customize>"
    assert mention_guild_navigation("browse", 222) == "<222:browse>"
    assert mention_guild_navigation("guide", 333) == "<333:guide>"
