"""Guild model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from byte_common.models.allowed_users_config import AllowedUsersConfig
    from byte_common.models.forum_config import ForumConfig
    from byte_common.models.github_config import GitHubConfig
    from byte_common.models.sotags_config import SOTagsConfig

__all__ = ("Guild",)


class Guild(UUIDAuditBase):
    """Guild configuration.

    A single guild will contain base defaults (e.g., ``prefix``, boolean flags for linking, etc.)
    with configurable options that can be set by the guild owner or ``allowed_users``.

    Part of the feature set of Byte is that you have interactivity with your git repositories,
    StackOverflow, Discord forums, and other external services.

    Here, a guild should be able to configure their own GitHub organization, StackOverflow tags, etc.
    """

    __tablename__ = "guild"  # type: ignore[reportAssignmentType]
    __table_args__ = {"comment": "Configuration for a Discord guild."}

    guild_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    guild_name: Mapped[str] = mapped_column(String(100))
    prefix: Mapped[str] = mapped_column(String(5), server_default="!", default="!")
    help_channel_id: Mapped[int | None] = mapped_column(BigInteger)
    showcase_channel_id: Mapped[int | None] = mapped_column(BigInteger)
    sync_label: Mapped[str | None]
    issue_linking: Mapped[bool] = mapped_column(default=False)
    comment_linking: Mapped[bool] = mapped_column(default=False)
    pep_linking: Mapped[bool] = mapped_column(default=False)

    # =================
    # ORM Relationships
    # =================
    github_config: Mapped[GitHubConfig | None] = relationship(
        lazy="noload",
        back_populates="guild",
        cascade="save-update, merge, delete",
    )
    sotags_configs: Mapped[list[SOTagsConfig]] = relationship(
        lazy="noload",
        back_populates="guild",
        cascade="all, delete-orphan",
    )
    allowed_users: Mapped[list[AllowedUsersConfig]] = relationship(
        lazy="noload",
        back_populates="guild",
        cascade="save-update, merge, delete",
    )
    forum_config: Mapped[ForumConfig | None] = relationship(
        lazy="noload",
        back_populates="guild",
        cascade="save-update, merge, delete",
    )
