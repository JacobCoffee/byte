"""Types for Astral views and plugins."""

from __future__ import annotations

from typing import TypedDict

__all__ = ("BaseRuffRule", "FormattedRuffRule", "RuffRule")


class BaseRuffRule(TypedDict):
    """Base Ruff rule data."""

    name: str
    summary: str
    fix: str
    explanation: str


class RuffRule(BaseRuffRule):
    """Ruff rule data."""

    code: str
    linter: str
    message_formats: list[str]
    preview: bool


class FormattedRuffRule(BaseRuffRule):
    """Formatted Ruff rule data."""

    rule_link: str
    rule_anchor_link: str
