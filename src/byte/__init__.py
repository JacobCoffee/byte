"""Byte Bot Bot."""
from __future__ import annotations

from src.byte import bot, lib
from src.byte.lib.logging import setup_logging

__all__ = ["bot", "lib"]

setup_logging()