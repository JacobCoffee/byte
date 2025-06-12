"""Shared models."""

from __future__ import annotations

from uuid import UUID  # noqa: TC003

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

__all__ = ("GitHubConfig", "Guild", "SOTagsConfig", "User", "AllowedUsersConfig", "ForumConfig")


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
        cascade="save-update, merge, delete",
    )


class SOTagsConfig(UUIDAuditBase):
    """SQLAlchemy association model for a guild's Stack Overflow tags config."""

    __tablename__ = "so_tags_config"  # type: ignore[reportAssignmentType]
    __table_args__ = (
        UniqueConstraint("guild_id", "tag_name"),
        {"comment": "Configuration for a Discord guild's Stack Overflow tags."},
    )

    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild.guild_id", ondelete="cascade"))
    guild_name: AssociationProxy[str] = association_proxy("guild", "guild_name")
    tag_name: Mapped[str] = mapped_column(String(50))

    # =================
    # ORM Relationships
    # =================
    guild: Mapped[Guild] = relationship(
        back_populates="sotags_configs",
        foreign_keys="SOTagsConfig.guild_id",
        innerjoin=True,
        lazy="noload",
    )


class AllowedUsersConfig(UUIDAuditBase):
    """SQLAlchemy association model for a guild's allowed users' config.

    A guild normally has a set of users to perform administrative actions, but sometimes
    we don't want to give full administrative access to a user.

    This model allows us to configure which users are allowed to perform administrative
    actions on Byte specifically without giving them full administrative access to the Discord guild.

    .. todo:: More preferably, this should be more generalized to a user OR role ID.
    """

    __tablename__ = "allowed_users"  # type: ignore[reportAssignmentType]
    __table_args__ = (
        UniqueConstraint("guild_id", "user_id"),
        {"comment": "Configuration for allowed users in a Discord guild."},
    )

    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild.guild_id", ondelete="cascade"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="cascade"))

    guild_name: AssociationProxy[str] = association_proxy("guild", "guild_name")
    user_name: AssociationProxy[str] = association_proxy("user", "name")

    # =================
    # ORM Relationships
    # =================
    guild: Mapped[Guild] = relationship(
        back_populates="allowed_users",
        foreign_keys="AllowedUsersConfig.guild_id",
        innerjoin=True,
        lazy="noload",
    )
    user: Mapped[User] = relationship(
        back_populates="guilds_allowed",
        foreign_keys="AllowedUsersConfig.user_id",
        innerjoin=True,
        lazy="noload",
    )


class User(UUIDAuditBase):
    """SQLAlchemy model representing a user.

    .. todo:: This may not really be needed?

    Currently, a user in the Byte context is an individual user assigned to the
    guild's allowed users config.

    In the future we may want to expand this to allow for more granular permissions.
    """

    __tablename__ = "user"  # type: ignore[reportAssignmentType]
    __table_args__ = {"comment": "A user."}

    name: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[str | None]
    discriminator: Mapped[str] = mapped_column(String(4))

    # =================
    # ORM Relationships
    # =================
    guilds_allowed: Mapped[list[AllowedUsersConfig]] = relationship(
        back_populates="user",
        lazy="noload",
        cascade="save-update, merge, delete",
    )


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

    """Help forum settings."""
    help_forum: Mapped[bool] = mapped_column(default=False)
    help_forum_category: Mapped[str | None]
    help_channel_id: Mapped[int | None] = association_proxy("guild", "help_channel_id")
    help_thread_auto_close: Mapped[bool] = mapped_column(default=False)
    help_thread_auto_close_days: Mapped[int | None]
    help_thread_notify: Mapped[bool] = mapped_column(default=False)
    help_thread_notify_roles: Mapped[str | None]
    help_thread_notify_days: Mapped[int | None]
    help_thread_sync: Mapped[bool] = association_proxy("guild", "github_config.discussion_sync")

    """Showcase forum settings."""
    showcase_forum: Mapped[bool] = mapped_column(default=False)
    showcase_forum_category: Mapped[str | None]
    showcase_channel_id: Mapped[int | None] = association_proxy("guild", "showcase_channel_Id")
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
