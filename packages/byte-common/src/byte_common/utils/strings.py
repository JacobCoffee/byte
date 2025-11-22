"""String utility functions."""

from __future__ import annotations

import re
import unicodedata

__all__ = [
    "camel_case",
    "case_insensitive_string_compare",
    "slugify",
]


def slugify(value: str, allow_unicode: bool = False, separator: str | None = None) -> str:
    """Convert a string to a slug.

    Args:
        value: The string to slugify.
        allow_unicode: Whether to allow unicode characters.
        separator: The separator to use.

    Returns:
        The slugified string.
    """
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    if separator is not None:
        return re.sub(r"[-\s]+", "-", value).strip("-_").replace("-", separator)
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def camel_case(string: str) -> str:
    """Convert a string to camel case.

    Args:
        string: The string to convert.

    Returns:
        The camel cased string.
    """
    return "".join(word if index == 0 else word.capitalize() for index, word in enumerate(string.split("_")))


def case_insensitive_string_compare(a: str, b: str, /) -> bool:
    """Compare two strings case insensitively.

    Args:
        a: The first string.
        b: The second string.

    Returns:
        Whether the strings are equal.
    """
    return a.strip().lower() == b.strip().lower()
