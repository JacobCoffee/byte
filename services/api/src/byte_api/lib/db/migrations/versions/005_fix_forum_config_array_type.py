# type: ignore
"""Revision ID: cd34267d1ffb
Revises: f32ee278015d
Create Date: 2025-11-23 16:53:17.780348+00:00

Fix ForumConfig.help_thread_notify_roles field type from String to ARRAY(BigInteger).
"""

from __future__ import annotations

import warnings

import sqlalchemy as sa
from advanced_alchemy.types import GUID, ORA_JSONB, DateTimeUTC
from alembic import op
from sqlalchemy import Text  # noqa: F401

from byte_common.models.forum_config import IntegerArray

__all__ = ["data_downgrades", "data_upgrades", "downgrade", "schema_downgrades", "schema_upgrades", "upgrade"]

sa.GUID = GUID
sa.DateTimeUTC = DateTimeUTC
sa.ORA_JSONB = ORA_JSONB

# revision identifiers, used by Alembic.
revision = "cd34267d1ffb"
down_revision = "f32ee278015d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        with op.get_context().autocommit_block():
            schema_upgrades()
            data_upgrades()


def downgrade() -> None:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        with op.get_context().autocommit_block():
            data_downgrades()
            schema_downgrades()


def schema_upgrades() -> None:
    """Schema upgrade migrations go here."""
    # Change help_thread_notify_roles from String to IntegerArray (ARRAY on PostgreSQL, JSON elsewhere)
    # Add help_thread_sync as a regular boolean field (was broken association proxy)
    with op.batch_alter_table("forum_config", schema=None) as batch_op:
        batch_op.alter_column(
            "help_thread_notify_roles",
            existing_type=sa.String(),
            type_=IntegerArray(),
            existing_nullable=True,
            postgresql_using="string_to_array(help_thread_notify_roles, ',')::bigint[]",
        )
        batch_op.add_column(sa.Column("help_thread_sync", sa.Boolean(), nullable=False, server_default="false"))


def schema_downgrades() -> None:
    """Schema downgrade migrations go here."""
    # Revert help_thread_notify_roles from IntegerArray back to String
    # Remove help_thread_sync field
    with op.batch_alter_table("forum_config", schema=None) as batch_op:
        batch_op.drop_column("help_thread_sync")
        batch_op.alter_column(
            "help_thread_notify_roles",
            existing_type=IntegerArray(),
            type_=sa.String(),
            existing_nullable=True,
            postgresql_using="array_to_string(help_thread_notify_roles, ',')",
        )


def data_upgrades() -> None:
    """Add any optional data upgrade migrations here!"""


def data_downgrades() -> None:
    """Add any optional data downgrade migrations here!"""
