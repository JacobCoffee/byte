"""Stack Overflow tags configuration model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from byte_common.models.guild import Guild

__all__ = ("SOTagsConfig",)


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
