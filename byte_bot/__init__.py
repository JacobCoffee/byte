"""Byte Bot."""

from __future__ import annotations

from rich import get_console
from rich.traceback import install as rich_tracebacks

from byte_bot import app, byte, cli, server, utils
from byte_bot.__metadata__ import __version__

__all__ = (
    "__version__",
    "app",
    "byte",
    "cli",
    "server",
    "utils",
)

rich_tracebacks(
    console=get_console(),
    suppress=(
        "click",
        "rich",
        "saq",
        "litestar",
        "rich_click",
    ),
    show_locals=False,
)
"""Pre-configured traceback handler.

Suppresses some of the frames by default to reduce the amount printed to
the screen.
"""
