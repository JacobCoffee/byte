"""Byte Bot Bot."""

from __future__ import annotations

from byte_bot.byte import bot, lib, plugins, views
from byte_bot.byte.lib.log import setup_logging

__all__ = ("bot", "lib", "views", "setup_logging", "plugins")

setup_logging()
