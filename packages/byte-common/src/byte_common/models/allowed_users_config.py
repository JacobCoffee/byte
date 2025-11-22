"""Allowed users configuration model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from byte_common.models.guild import Guild
    from byte_common.models.user import User

__all__ = ("AllowedUsersConfig",)


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
