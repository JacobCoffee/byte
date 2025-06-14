"""Types for Python related views and plugins."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from datetime import datetime

__all__ = ("PEP", "PEPHistoryItem", "PEPStatus", "PEPType")


class PEPType(StrEnum):
    """Type of PEP.

    Based off of `PEP Types in PEP1 <https://peps.python.org/#pep-types-key>`_.
    """

    I = "Informational"  # noqa: E741
    P = "Process"
    S = "Standards Track"


class PEPStatus(StrEnum):
    """Status of a PEP.

    .. note:: ``Active`` and ``Accepted`` both traditionally use ``A``,
        but are differentiated here for clarity.

    Based off of `PEP Status in PEP1 <https://peps.python.org/#pep-status-key>`_.
    """

    A = "Active"
    AA = "Accepted"
    D = "Deferred"
    __ = "Draft"
    F = "Final"
    P = "Provisional"
    R = "Rejected"
    S = "Superseded"
    W = "Withdrawn"


class PEPHistoryItem(TypedDict, total=False):
    """PEP history item.

    Sometimes these include a list of ``datetime`` objects,
    other times they are a list of datetime and str
    because they contain a date and an rST link.
    """

    date: str
    link: str


class PEP(TypedDict):
    """PEP data.

    Based off of the `PEPS API <https://peps.python.org/api/peps.json>`_.
    """

    number: int
    title: str
    authors: list[str] | str
    discussions_to: str
    status: PEPStatus
    type: PEPType
    topic: str
    created: datetime
    python_version: list[float] | float
    post_history: list[str]
    resolution: str | None
    requires: str | None
    replaces: str | None
    superseded_by: str | None
    url: str
