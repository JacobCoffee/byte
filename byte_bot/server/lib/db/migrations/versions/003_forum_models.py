# type: ignore
"""
Revision ID: 73a26ceab2c4
Revises: feebdacfdd91
Create Date: 2024-03-10 22:30:54.150566+00:00
"""

from __future__ import annotations

import warnings

import sqlalchemy as sa
from advanced_alchemy.types import GUID, ORA_JSONB, DateTimeUTC
from alembic import op
from sqlalchemy import Text  # noqa: F401

__all__ = ["data_downgrades", "data_upgrades", "downgrade", "schema_downgrades", "schema_upgrades", "upgrade"]

sa.GUID = GUID
sa.DateTimeUTC = DateTimeUTC
sa.ORA_JSONB = ORA_JSONB

# revision identifiers, used by Alembic.
revision = "73a26ceab2c4"
down_revision = "feebdacfdd91"
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
    """schema upgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "forum_config",
        sa.Column("id", sa.GUID(length=16), nullable=False),
        sa.Column("guild_id", sa.GUID(length=16), nullable=False),
        sa.Column("help_forum", sa.Boolean(), nullable=False),
        sa.Column("help_forum_category", sa.String(), nullable=True),
        sa.Column("help_thread_auto_close", sa.Boolean(), nullable=False),
        sa.Column("help_thread_auto_close_days", sa.Integer(), nullable=True),
        sa.Column("help_thread_notify", sa.Boolean(), nullable=False),
        sa.Column("help_thread_notify_roles", sa.String(), nullable=True),
        sa.Column("help_thread_notify_days", sa.Integer(), nullable=True),
        sa.Column("showcase_forum", sa.Boolean(), nullable=False),
        sa.Column("showcase_forum_category", sa.String(), nullable=True),
        sa.Column("showcase_thread_auto_close", sa.Boolean(), nullable=False),
        sa.Column("showcase_thread_auto_close_days", sa.Integer(), nullable=True),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["guild_id"], ["guild.id"], name=op.f("fk_forum_config_guild_id_guild"), ondelete="cascade"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_forum_config")),
    )
    with op.batch_alter_table("allowed_users", schema=None) as batch_op:
        batch_op.create_table_comment("Configuration for allowed users in a Discord guild.", existing_comment=None)

    with op.batch_alter_table("guild", schema=None) as batch_op:
        batch_op.add_column(sa.Column("showcase_channel_id", sa.BigInteger(), nullable=True))
        batch_op.create_table_comment("Configuration for a Discord guild.", existing_comment=None)

    with op.batch_alter_table("so_tags", schema=None) as batch_op:
        batch_op.create_table_comment("Configuration for a Discord guild's Stack Overflow tags.", existing_comment=None)

    # ### end Alembic commands ###


def schema_downgrades() -> None:
    """schema downgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("so_tags", schema=None) as batch_op:
        batch_op.drop_table_comment(existing_comment="Configuration for a Discord guild's Stack Overflow tags.")

    with op.batch_alter_table("guild", schema=None) as batch_op:
        batch_op.drop_table_comment(existing_comment="Configuration for a Discord guild.")
        batch_op.drop_column("showcase_channel_id")

    with op.batch_alter_table("allowed_users", schema=None) as batch_op:
        batch_op.drop_table_comment(existing_comment="Configuration for allowed users in a Discord guild.")

    op.drop_table("forum_config")
    # ### end Alembic commands ###


def data_upgrades() -> None:
    """Add any optional data upgrade migrations here!"""


def data_downgrades() -> None:
    """Add any optional data downgrade migrations here!"""
