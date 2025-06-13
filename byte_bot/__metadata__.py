"""Source of truth for project metadata."""

from __future__ import annotations

import importlib.metadata

__all__ = ("__project__", "__version__")

__version__ = importlib.metadata.version("byte-bot")
"""Version of the app."""
__project__ = importlib.metadata.metadata("byte-bot")["Name"]
"""Name of the app."""
