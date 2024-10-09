"""Byte Bot."""
from __future__ import annotations

from rich import get_console
from rich.traceback import install as rich_tracebacks

from src.__metadata__ import __version__
from src import app, byte, cli, server, utils

__all__ = (
    "__version__",
    "app",
    "cli",
    "utils",
    "byte",
    "server",
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
