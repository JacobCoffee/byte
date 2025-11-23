"""Bot service entrypoint."""

from __future__ import annotations

import sys

__all__ = ("main",)


def main() -> None:
    """Run the Discord bot."""
    try:
        from byte_bot.bot import run_bot  # noqa: PLC0415
    except ImportError as exc:
        print(  # noqa: T201
            "Could not load required libraries. "
            "Please check your installation and make sure you activated any necessary virtual environment.",
        )
        print(exc)  # noqa: T201
        sys.exit(1)

    # Run the bot
    run_bot()


if __name__ == "__main__":
    main()
