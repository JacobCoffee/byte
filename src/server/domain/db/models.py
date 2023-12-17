"""Shared models."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.lib.db.orm import DatabaseModel, TimestampedDatabaseModel

__all__ = (
    "GitHubConfig",
    "GuildConfig",
    "GuildGitHubConfig",
    "GuildSOTagsConfig",
    "SOTagConfig",
    "User",
    "GuildAllowedUsersConfig",
)


class GuildConfig(TimestampedDatabaseModel):
    """Guild configuration.

    A single guild will contain base defaults (e.g., ``prefix``, boolean flags for linking, etc.)
    with configurable options that can be set by the guild owner or ``allowed_users``.

    Part of the feature set of Byte is that you have interactivity with your git repositories,
    StackOverflow, Discord forums, and other external services.

    Here, a guild should be able to configure their own GitHub organization, StackOverflow tags, etc.
    """

    __tablename__ = "guild_config"
    __table_args__ = {"comment": "Configuration for a Discord guild."}

    guild_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    guild_name: Mapped[str] = mapped_column(String(100))
    prefix: Mapped[str] = mapped_column(String(5), server_default="!", default="!")
    help_channel_id: Mapped[int] = mapped_column(BigInteger, index=True)
    sync_label: Mapped[str | None]
    issue_linking: Mapped[bool] = mapped_column(default=False)
    comment_linking: Mapped[bool] = mapped_column(default=False)
    pep_linking: Mapped[bool] = mapped_column(default=False)

    # =================
    # ORM Relationships
    # =================
    github_config: Mapped[GitHubConfig] = relationship(
        lazy="noload",
        back_populates="guild_config",
        cascade="save-update, merge, delete",
    )
    sotags_config: Mapped[list[SOTagConfig]] = relationship(
        lazy="noload",
        back_populates="guild_config",
        cascade="save-update, merge, delete",
    )
    allowed_users_config: Mapped[list[GuildAllowedUsersConfig]] = relationship(
        lazy="noload",
        back_populates="guild_config",
        cascade="save-update, merge, delete",
    )


class GuildGitHubConfig(UUIDAuditBase):
    """SQLAlchemy association model representing a guild's unique GitHub config."""

    __tablename__ = "guild_github_config"
    __table_args__ = (
        UniqueConstraint("guild_id", "github_config_id"),
        {"comment": "Configuration for a Discord guild."},
    )

    guild_id: Mapped[int] = mapped_column(ForeignKey("guild_config.guild_id", ondelete="cascade"))
    github_config_id: Mapped[UUID] = mapped_column(ForeignKey("github_config.id", ondelete="cascade"))

    guild_name: AssociationProxy[str] = association_proxy("guild_config", "guild_name")
    github_organization: AssociationProxy[str | None] = association_proxy("github_config", "github_organization")

    # =================
    # ORM Relationships
    # =================
    guild_config: Mapped[GuildConfig] = relationship(
        back_populates="github_config",
        foreign_keys="GuildGitHubConfig.guild_id",
        innerjoin=True,
        lazy="noload",
    )
    github_config: Mapped[GitHubConfig] = relationship(
        back_populates="guild_config",
        foreign_keys="GuildGitHubConfig.github_config_id",
        innerjoin=True,
        lazy="noload",
    )


class GitHubConfig(TimestampedDatabaseModel):
    """GitHub configuration.

    A guild will be able to configure which organization or user they want as a default
    base, which repository they want as a default, and whether they would like to sync
    discussions with forum posts.
    """

    __tablename__ = "github_config"
    __table_args__ = {"comment": "GitHub configuration for a guild."}

    discussion_sync: Mapped[bool] = mapped_column(default=False)
    github_organization: Mapped[str | None]
    github_repository: Mapped[str | None]

    # =================
    # ORM Relationships
    # =================
    guild_config: Mapped[GuildGitHubConfig] = relationship(
        back_populates="github_config",
        lazy="noload",
        cascade="save-update, merge, delete",
    )


class GuildSOTagsConfig(UUIDAuditBase):
    """SQLAlchemy association model for a guild's Stack Overflow tags config."""

    __tablename__ = "guild_sotags_config"
    __table_args__ = (
        UniqueConstraint("guild_id", "sotag_config_id"),
        {"comment": "Configuration for a Discord guild's Stack Overflow tags."},
    )

    guild_id: Mapped[int] = mapped_column(ForeignKey("guild_config.guild_id", ondelete="cascade"))
    sotag_config_id: Mapped[UUID] = mapped_column(ForeignKey("sotag_config.id", ondelete="cascade"))

    guild_name: AssociationProxy[str] = association_proxy("guild_config", "guild_name")
    tag_name: AssociationProxy[str] = association_proxy("sotag_config", "tag_name")

    # =================
    # ORM Relationships
    # =================
    guild_config: Mapped[GuildConfig] = relationship(
        back_populates="sotags_config",
        foreign_keys="GuildSOTagsConfig.guild_id",
        innerjoin=True,
        lazy="noload",
    )
    sotag_config: Mapped[SOTagConfig] = relationship(
        back_populates="guild_config",
        foreign_keys="GuildSOTagsConfig.sotag_config_id",
        innerjoin=True,
        lazy="noload",
    )


class SOTagConfig(DatabaseModel):
    """Stack Overflow tag configuration.

    A guild will be able to configure which Stack Overflow tags they want to monitor
    and report on. Byte will then utilize the StackOverflow API to fetch new questions
    and post them to the guild's configured channel.
    """

    __tablename__ = "sotag_config"
    __table_args__ = {"comment": "Configuration for Stack Overflow tags."}

    tag_name: Mapped[str] = mapped_column(String(50))

    # =================
    # ORM Relationships
    # =================
    guild_config: Mapped[GuildSOTagsConfig] = relationship(
        back_populates="sotag_config",
        lazy="noload",
        cascade="save-update, merge, delete",
    )


class GuildAllowedUsersConfig(UUIDAuditBase):
    """SQLAlchemy association model for a guild's allowed users' config.

    A guild normally has a set of users to perform administrative actions, but sometimes
    we don't want to give full administrative access to a user.

    This model allows us to configure which users are allowed to perform administrative
    actions on Byte specifically without giving them full administrative access to the Discord guild.
    """

    __tablename__ = "guild_allowed_users_config"
    __table_args__ = (
        UniqueConstraint("guild_id", "user_id"),
        {"comment": "Configuration for allowed users in a Discord guild."},
    )

    guild_id: Mapped[int] = mapped_column(ForeignKey("guild_config.guild_id", ondelete="cascade"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="cascade"))

    guild_name: AssociationProxy[str] = association_proxy("guild_config", "guild_name")
    user_name: AssociationProxy[str] = association_proxy("user", "name")

    # =================
    # ORM Relationships
    # =================
    guild_config: Mapped[GuildConfig] = relationship(
        back_populates="allowed_users_config",
        foreign_keys="GuildAllowedUsersConfig.guild_id",
        innerjoin=True,
        lazy="noload",
    )
    user: Mapped[User] = relationship(
        back_populates="guilds_allowed",
        foreign_keys="GuildAllowedUsersConfig.user_id",
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

    __tablename__ = "user"
    __table_args__ = {"comment": "A user."}

    name: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[str | None]
    discriminator: Mapped[str] = mapped_column(String(4))

    # =================
    # ORM Relationships
    # =================
    guilds_allowed: Mapped[list[GuildAllowedUsersConfig]] = relationship(
        back_populates="user",
        lazy="noload",
        cascade="save-update, merge, delete",
    )
