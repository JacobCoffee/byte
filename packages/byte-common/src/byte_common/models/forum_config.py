"""Forum configuration model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import JSON, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

if TYPE_CHECKING:
    from sqlalchemy.engine import Dialect

    from byte_common.models.guild import Guild

__all__ = ("ForumConfig", "IntegerArray")


class IntegerArray(TypeDecorator):
    """Platform-independent integer array type.

    Uses ARRAY on PostgreSQL and JSON on other databases.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        """Load dialect-specific type implementation.

        Args:
            dialect: Database dialect instance

        Returns:
            Any: Type descriptor for the dialect (ARRAY or JSON)
        """
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(BigInteger))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value: list[int] | None, dialect: Dialect) -> list[int] | None:
        """Process value before binding to database.

        Args:
            value: List of integers or None
            dialect: Database dialect instance

        Returns:
            list[int] | None: Processed value
        """
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        # For JSON, ensure it's a list
        return value if isinstance(value, list) else []

    def process_result_value(self, value: list[int] | None, _dialect: Dialect) -> list[int]:
        """Process value after fetching from database.

        Args:
            value: List of integers or None
            _dialect: Database dialect instance (unused)

        Returns:
            list[int]: Empty list if None, otherwise the value
        """
        if value is None:
            return []
        return value if isinstance(value, list) else []


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
    help_thread_auto_close: Mapped[bool] = mapped_column(default=False)
    help_thread_auto_close_days: Mapped[int | None]
    help_thread_notify: Mapped[bool] = mapped_column(default=False)
    help_thread_notify_roles: Mapped[list[int]] = mapped_column(IntegerArray, default=list)
    help_thread_notify_days: Mapped[int | None]
    help_thread_sync: Mapped[bool] = mapped_column(default=False)

    # Showcase forum settings
    showcase_forum: Mapped[bool] = mapped_column(default=False)
    showcase_forum_category: Mapped[str | None]
    showcase_thread_auto_close: Mapped[bool] = mapped_column(default=False)
    showcase_thread_auto_close_days: Mapped[int | None]

    # =================
    # ORM Relationships
    # =================
    guild: Mapped[Guild] = relationship(
        back_populates="forum_config",
        innerjoin=True,
        lazy="noload",
        cascade="save-update, merge",
    )
