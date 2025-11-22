"""Encoding utility functions."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["encode_to_base64"]


def encode_to_base64(file: Path) -> str:
    """Encode a file to base64.

    Args:
        file: The path to the file to encode.

    Returns:
        The base64-encoded contents of the file.
    """
    file_contents = file.read_bytes()
    encoded_contents = base64.b64encode(file_contents)
    return encoded_contents.decode("utf-8")
