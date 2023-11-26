"""Shared models."""

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.server.lib.db.orm import TimestampedDatabaseModel

__all__ = ("GitHubConfig", "GuildConfig", "Role")


allowed_roles_table = Table(
    "allowed_roles",
    TimestampedDatabaseModel.metadata,
    mapped_column("github_config_id", ForeignKey("github_configs.id"), primary_key=True),
    mapped_column("role_id", BigInteger, primary_key=True),
)


class GuildConfig(TimestampedDatabaseModel):
    """Guild configuration."""

    __tablename__ = "guild_configs"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    prefix: Mapped[str] = mapped_column(String(5), nullable=False, server_default="!", default="!")

    help_channel_id: Mapped[int] = mapped_column(BigInteger, index=True)
    github_config: Mapped["GitHubConfig"] = relationship("GitHubConfig", uselist=False, back_populates="guild_config")


class GitHubConfig(TimestampedDatabaseModel):
    """GitHub configuration."""

    __tablename__ = "github_configs"

    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_configs.guild_id"), nullable=False)
    discussion_sync: Mapped[bool] = mapped_column(Boolean, default=False)
    github_organization: Mapped[str | None] = mapped_column(String)
    github_repository: Mapped[str | None] = mapped_column(String)
    sync_label: Mapped[str | None] = mapped_column(String)
    issue_linking: Mapped[bool] = mapped_column(Boolean, default=False)
    comment_linking: Mapped[bool] = mapped_column(Boolean, default=False)
    pep_linking: Mapped[bool] = mapped_column(Boolean, default=False)

    allowed_roles: Mapped[list[int]] = relationship(
        "Role",
        secondary=allowed_roles_table,
        back_populates="github_configs",
    )

    guild_config: Mapped[GuildConfig] = relationship("GuildConfig", back_populates="github_config")


class Role(TimestampedDatabaseModel):
    """Role."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # noqa: A003

    github_configs: Mapped[list[GitHubConfig]] = relationship(
        "GitHubConfig",
        secondary=allowed_roles_table,
        back_populates="allowed_roles",
    )
