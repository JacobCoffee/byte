"""Database migration script for production deployments.

This script applies all pending Alembic migrations to the database.
It's designed to be run before starting the application in production environments.
"""

from __future__ import annotations

import sys

from advanced_alchemy.alembic.commands import AlembicCommands

from byte_api.lib.db.base import config

__all__ = ("main",)


def main() -> int:
    """Run database migrations.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("Running database migrations...")  # noqa: T201
    try:
        alembic = AlembicCommands(sqlalchemy_config=config)
        alembic.upgrade()
    except Exception as e:  # noqa: BLE001
        print(f"Migration failed: {e}", file=sys.stderr)  # noqa: T201
        return 1
    else:
        print("Migrations complete!")  # noqa: T201
        return 0


if __name__ == "__main__":
    sys.exit(main())
