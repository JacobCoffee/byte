"""GitHub configuration model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from byte_common.models.guild import Guild

__all__ = ("GitHubConfig",)


class GitHubConfig(UUIDAuditBase):
    """GitHub configuration.

    A guild will be able to configure which organization or user they want as a default
    base, which repository they want as a default, and whether they would like to sync
    discussions with forum posts.
    """

    __tablename__ = "github_config"  # type: ignore[reportAssignmentType]
    __table_args__ = {"comment": "GitHub configuration for a guild."}

    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild.guild_id", ondelete="cascade"))
    discussion_sync: Mapped[bool] = mapped_column(default=False)
    github_organization: Mapped[str | None]
    github_repository: Mapped[str | None]

    # =================
    # ORM Relationships
    # =================
    guild: Mapped[Guild] = relationship(
        back_populates="github_config",
        innerjoin=True,
        lazy="noload",
        cascade="save-update, merge",
    )
