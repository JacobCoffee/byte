"""General utility functions."""

from __future__ import annotations

import base64
import dataclasses
import re
import sys
import unicodedata
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Any

__all__ = [
    "camel_case",
    "case_insensitive_string_compare",
    "dataclass_as_dict_shallow",
    "import_string",
    "slugify",
]

if TYPE_CHECKING:
    from types import ModuleType


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


def dataclass_as_dict_shallow(dataclass: Any, *, exclude_none: bool = False) -> dict[str, Any]:
    """Convert a dataclass to a dict.

    Args:
        dataclass: The dataclass to convert.
        exclude_none: Whether to exclude None values.

    Returns:
        The dataclass as a dict.
    """
    ret: dict[str, Any] = {}
    for field in dataclasses.fields(dataclass):
        value = getattr(dataclass, field.name)
        if exclude_none and value is None:
            continue
        ret[field.name] = value
    return ret


def import_string(dotted_path: str) -> Any:
    """Import a class/function from a dotted path.

    Args:
        dotted_path: The dotted path to the class/function.

    Returns:
        The imported class/function.
    """

    def _is_loaded(module: ModuleType | None) -> bool:
        """Check if a module is loaded.

        Args:
            module: The module to check.

        Returns:
            Whether the module is loaded.
        """
        spec = getattr(module, "__spec__", None)
        initializing = getattr(spec, "_initializing", False)
        return bool(module and spec and not initializing)

    def _cached_import(module_path: str, class_name: str) -> Any:
        """Import a class/function from a dotted path.

        Args:
            module_path: The dotted path to the module.
            class_name: The name of the class/function.

        Returns:
            The imported class/function.
        """
        module = sys.modules.get(module_path)
        if not _is_loaded(module):
            module = import_module(module_path)
        return getattr(module, class_name)

    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as e:
        msg = "%s doesn't look like a module path"
        raise ImportError(msg, dotted_path) from e

    try:
        return _cached_import(module_path, class_name)
    except AttributeError as e:
        msg = "Module '%s' does not define a '%s' attribute/class"
        raise ImportError(msg, module_path, class_name) from e


def encode_to_base64(file: Path) -> str:
    """Encode a file to base64.

    Args:
        file: The path to the PEM file.

    Returns:
        The encoded contents of the PEM file.
    """
    pem_contents = file.read_bytes()
    encoded_contents = base64.b64encode(pem_contents)
    return encoded_contents.decode("utf-8")
