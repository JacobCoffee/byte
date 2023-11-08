"""Shared models.

.. todo:: This is mostly a stub package that needs to be
    fleshed out.
"""

# from sqlalchemy import BigInteger, Boolean, ForeignKey, String, Table
# from sqlalchemy.orm import Mapped, mapped_column, relationship
#
# from src.database.orm import TimestampedDatabaseModel
#
# allowed_roles_table = Table(
#     "allowed_roles",
#     TimestampedDatabaseModel.metadata,
#     mapped_column("github_config_id", ForeignKey("github_configs.id"), primary_key=True),
#     mapped_column("role_id", BigInteger, primary_key=True),
# )
#
#
# class GuildConfig(TimestampedDatabaseModel):
#     __tablename__ = "guild_configs"
#
#     guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
#     prefix: Mapped[str] = mapped_column(String(5), nullable=False, server_default="!", de
#
#     help_channel_id: Mapped[int] = mapped_column(BigInteger, index=True)
#     github_config: Mapped["GitHubConfig"] = relationship("GitHubConfig", uselist=False, back_populates="guild_config")
#
#
# class GitHubConfig(TimestampedDatabaseModel):
#     __tablename__ = "github_configs"
#
#     guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guild_configs.guild_id"), nullable=False)
#     discussion_sync: Mapped[bool] = mapped_column(Boolean, default=False)
#     github_organization: Mapped[str] = mapped_column(String, nullable=True)
#     github_repository: Mapped[str] = mapped_column(String, nullable=True)
#     sync_label: Mapped[str] = mapped_column(String, nullable=True)
#     issue_linking: Mapped[bool] = mapped_column(Boolean, default=False)
#     comment_linking: Mapped[bool] = mapped_column(Boolean, default=False)
#     pep_linking: Mapped[bool] = mapped_column(Boolean, default=False)
#
#     allowed_roles: Mapped[list[int]] = relationship(
#         "Role",
#         secondary=allowed_roles_table,
#         back_populates="github_configs",
#     )
#
#     guild_config: Mapped[GuildConfig] = relationship("GuildConfig", back_populates="github_config")
#
#
# class Role(TimestampedDatabaseModel):
#     __tablename__ = "roles"
#
#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
#
#     github_configs: Mapped[list[GitHubConfig]] = relationship(
#         "GitHubConfig",
#         secondary=allowed_roles_table,
#         back_populates="allowed_roles",
#     )
