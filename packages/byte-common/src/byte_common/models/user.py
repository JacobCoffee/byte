"""User model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from byte_common.models.allowed_users_config import AllowedUsersConfig

__all__ = ("User",)


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
