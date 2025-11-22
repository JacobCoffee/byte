"""Forum configuration model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from byte_common.models.guild import Guild

__all__ = ("ForumConfig",)


class ForumConfig(UUIDAuditBase):
    """Forum configuration.

    A guild will be able to set whether they want help and/or showcase forums.
        * If they already have them set up, they can configure the channel IDs for them.
        * If they don't have them set up, they can configure the category and channel names for them
          Byte will then create the channels for them.
        * If they don't want them, they can disable them.

    Help forum settings include:
        * Respond with help embed, including a link to 'Open a GitHub Issue'
          if the `GitHubConfig:github_organization` and `GitHubConfig:github_repository` are set.
          Also includes `Solve` button to mark as solved and close the thread.
        * Automatic thread closing after a certain period of inactivity.
        * Uploading of threads into GitHub discussions.
        * Pinging of defined roles when a thread has not received a response from someone with those roles
          after a certain period of time.

    Showcase forum settings include:
        * Respond with showcase embed, including a link to 'Add to awesome-$repo'
          if the `GitHubConfig:github_organization` and `GitHubConfig:github_awesome` are set.
        * Automatic thread closing after a certain period of inactivity.
        * Uploading of threads into GitHub discussions.
    """

    __tablename__ = "forum_config"  # type: ignore[reportAssignmentType]
    __table_args__ = {"comment": "Forum configuration for a guild."}

    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild.guild_id", ondelete="cascade"))

    # Help forum settings
    help_forum: Mapped[bool] = mapped_column(default=False)
    help_forum_category: Mapped[str | None]
    help_channel_id: AssociationProxy[int | None] = association_proxy("guild", "help_channel_id")
    help_thread_auto_close: Mapped[bool] = mapped_column(default=False)
    help_thread_auto_close_days: Mapped[int | None]
    help_thread_notify: Mapped[bool] = mapped_column(default=False)
    help_thread_notify_roles: Mapped[str | None]
    help_thread_notify_days: Mapped[int | None]
    help_thread_sync: AssociationProxy[bool] = association_proxy("guild", "github_config.discussion_sync")

    # Showcase forum settings
    showcase_forum: Mapped[bool] = mapped_column(default=False)
    showcase_forum_category: Mapped[str | None]
    showcase_channel_id: AssociationProxy[int | None] = association_proxy("guild", "showcase_channel_Id")
    showcase_thread_auto_close: Mapped[bool] = mapped_column(default=False)
    showcase_thread_auto_close_days: Mapped[int | None]

    # =================
    # ORM Relationships
    # =================
    guild: Mapped[Guild] = relationship(
        back_populates="forum_config",
        innerjoin=True,
        lazy="noload",
        cascade="save-update, merge, delete",
    )
