# type: ignore
"""Revision ID: 43165a559e89
Revises:
Create Date: 2023-11-26 20:11:48.777676+00:00

"""
from __future__ import annotations

import warnings

import sqlalchemy as sa
from advanced_alchemy.types import GUID, ORA_JSONB, DateTimeUTC
from alembic import op
from sqlalchemy import Text  # noqa: F401

__all__ = ["downgrade", "upgrade", "schema_upgrades", "schema_downgrades", "data_upgrades", "data_downgrades"]

sa.GUID = GUID
sa.DateTimeUTC = DateTimeUTC
sa.ORA_JSONB = ORA_JSONB

# revision identifiers, used by Alembic.
revision = "43165a559e89"
down_revision = None
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
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "github_config",
        sa.Column("id", sa.GUID(length=16), nullable=False),
        sa.Column("discussion_sync", sa.Boolean(), nullable=False),
        sa.Column("github_organization", sa.String(), nullable=True),
        sa.Column("github_repository", sa.String(), nullable=True),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_github_config")),
    )
    op.create_table(
        "guild_config",
        sa.Column("id", sa.GUID(length=16), nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("guild_name", sa.String(length=100), nullable=False),
        sa.Column("prefix", sa.String(length=5), server_default="!", nullable=False),
        sa.Column("help_channel_id", sa.BigInteger(), nullable=False),
        sa.Column("sync_label", sa.String(), nullable=True),
        sa.Column("issue_linking", sa.Boolean(), nullable=False),
        sa.Column("comment_linking", sa.Boolean(), nullable=False),
        sa.Column("pep_linking", sa.Boolean(), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_guild_config")),
    )
    with op.batch_alter_table("guild_config", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_guild_config_guild_id"), ["guild_id"], unique=True)
        batch_op.create_index(batch_op.f("ix_guild_config_help_channel_id"), ["help_channel_id"], unique=False)

    op.create_table(
        "sotag_config",
        sa.Column("id", sa.GUID(length=16), nullable=False),
        sa.Column("tag_name", sa.String(length=50), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sotag_config")),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.GUID(length=16), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("discriminator", sa.String(length=4), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
    )
    op.create_table(
        "guild_allowed_users_config",
        sa.Column("id", sa.GUID(length=16), nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.GUID(length=16), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["guild_id"],
            ["guild_config.guild_id"],
            name=op.f("fk_guild_allowed_users_config_guild_id_guild_config"),
            ondelete="cascade",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_guild_allowed_users_config_user_id_user"), ondelete="cascade"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_guild_allowed_users_config")),
        sa.UniqueConstraint("guild_id", "user_id", name=op.f("uq_guild_allowed_users_config_guild_id")),
    )
    op.create_table(
        "guild_github_config",
        sa.Column("id", sa.GUID(length=16), nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("github_config_id", sa.GUID(length=16), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["github_config_id"],
            ["github_config.id"],
            name=op.f("fk_guild_github_config_github_config_id_github_config"),
            ondelete="cascade",
        ),
        sa.ForeignKeyConstraint(
            ["guild_id"],
            ["guild_config.guild_id"],
            name=op.f("fk_guild_github_config_guild_id_guild_config"),
            ondelete="cascade",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_guild_github_config")),
        sa.UniqueConstraint("guild_id", "github_config_id", name=op.f("uq_guild_github_config_guild_id")),
    )
    op.create_table(
        "guild_sotags_config",
        sa.Column("id", sa.GUID(length=16), nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("sotag_config_id", sa.GUID(length=16), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["guild_id"],
            ["guild_config.guild_id"],
            name=op.f("fk_guild_sotags_config_guild_id_guild_config"),
            ondelete="cascade",
        ),
        sa.ForeignKeyConstraint(
            ["sotag_config_id"],
            ["sotag_config.id"],
            name=op.f("fk_guild_sotags_config_sotag_config_id_sotag_config"),
            ondelete="cascade",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_guild_sotags_config")),
        sa.UniqueConstraint("guild_id", "sotag_config_id", name=op.f("uq_guild_sotags_config_guild_id")),
    )
    # ### end Alembic commands ###


def schema_downgrades() -> None:
    """Schema downgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("guild_sotags_config")
    op.drop_table("guild_github_config")
    op.drop_table("guild_allowed_users_config")
    op.drop_table("user")
    op.drop_table("sotag_config")
    with op.batch_alter_table("guild_config", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_guild_config_help_channel_id"))
        batch_op.drop_index(batch_op.f("ix_guild_config_guild_id"))

    op.drop_table("guild_config")
    op.drop_table("github_config")
    # ### end Alembic commands ###


def data_upgrades() -> None:
    """Add any optional data upgrade migrations here!"""


def data_downgrades() -> None:
    """Add any optional data downgrade migrations here!"""
