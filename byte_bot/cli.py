"""Project CLI."""

from __future__ import annotations

import multiprocessing
import subprocess
import sys
from typing import Any

import click
from rich import get_console

from byte_bot.server.lib import log, settings

__all__ = [
    "run_bot",
    "run_web",
    "run_all",
]

console = get_console()
"""Pre-configured CLI Console."""

logger = log.get_logger()


def frontend() -> None:
    """Run the tailwind compiler."""
    log.config.configure()
    logger.info("🎨 Starting Tailwind Compiler.")
    try:
        subprocess.run(
            [  # noqa: S603, S607
                "tailwindcss",
                "-i",
                "byte_bot/server/domain/web/resources/input.css",
                "-o",
                "byte_bot/server/domain/web/resources/style.css",
                "--watch",
            ],
            check=True,
        )
    finally:
        for process in multiprocessing.active_children():
            process.terminate()
        logger.info("🎨 Tailwind Compiler Shutdown complete")
        sys.exit()


def bot() -> None:
    """Run the bot."""
    log.config.configure()
    logger.info("🤖 Starting Byte.")
    try:
        subprocess.run(["python", "byte_bot/byte/bot.py"], check=True)  # noqa: S603, S607
    finally:
        for process in multiprocessing.active_children():
            process.terminate()
        logger.info("🤖 Byte Bot Shutdown complete")
        sys.exit()


@click.group(name="run-bot", invoke_without_command=True, help="Starts the bot.")
def run_bot() -> None:
    """Run the bot."""
    bot_process = multiprocessing.Process(target=bot)
    bot_process.start()
    bot_process.join()


def web(
    host: str,
    port: int | None,
    http_workers: int | None,
    reload: bool | None,
    verbose: bool | None,
    debug: bool | None,
) -> None:
    """Run the API server."""
    log.config.configure()
    settings.server.HOST = host or settings.server.HOST
    settings.server.PORT = port or settings.server.PORT
    settings.server.RELOAD = reload or settings.server.RELOAD if settings.server.RELOAD is not None else None
    settings.server.HTTP_WORKERS = http_workers or settings.server.HTTP_WORKERS
    settings.project.DEBUG = debug or settings.project.DEBUG
    settings.log.LEVEL = 10 if verbose or settings.project.DEBUG else settings.log.LEVEL

    try:
        logger.info("🖥️ Starting Litestar Web Server.")
        reload_dirs = settings.server.RELOAD_DIRS if settings.server.RELOAD else None
        process_args = {
            "reload": bool(settings.server.RELOAD),
            "host": settings.server.HOST,
            "port": settings.server.PORT,
            "workers": 1 if bool(settings.server.RELOAD or settings.project.DEV_MODE) else settings.server.HTTP_WORKERS,
            "factory": settings.server.APP_LOC_IS_FACTORY,
            "loop": "uvloop",
            "no-access-log": True,
            "timeout-keep-alive": settings.server.KEEPALIVE,
        }
        if reload_dirs:
            process_args["reload-dir"] = " ".join(reload_dirs)
        subprocess.run(
            ["uvicorn", settings.server.APP_LOC, *_convert_uvicorn_args(process_args)],  # noqa: S603, S607
            check=True,
        )
    finally:
        for process in multiprocessing.active_children():
            process.terminate()
        logger.info("🖥️ Server Shutdown complete")
        sys.exit()


@click.group(name="run-web", invoke_without_command=True, help="Starts the application server.")
@click.option(
    "-H",
    "--host",
    help="Host interface to listen on. Use 0.0.0.0 for all available interfaces.",
    type=click.STRING,
    default=settings.server.HOST,
    required=False,
    show_default=True,
)
@click.option(
    "-p",
    "--port",
    help="Port to bind.",
    type=click.INT,
    default=settings.server.PORT,
    required=False,
    show_default=True,
)
@click.option(
    "-W",
    "--http-workers",
    help="The number of HTTP worker processes for handling requests.",
    type=click.IntRange(min=1, max=multiprocessing.cpu_count() + 1),
    default=multiprocessing.cpu_count() + 1,
    required=False,
    show_default=True,
)
@click.option("-r", "--reload", help="Enable reload", is_flag=True, default=False, type=bool)
@click.option("-v", "--verbose", help="Enable verbose logging.", is_flag=True, default=False, type=bool)
@click.option("-d", "--debug", help="Enable debugging.", is_flag=True, default=False, type=bool)
def run_web(
    host: str,
    port: int | None,
    http_workers: int | None,
    reload: bool | None,
    verbose: bool | None,
    debug: bool | None,
) -> None:
    """Run the API server."""
    web_process = multiprocessing.Process(target=web, args=(host, port, http_workers, reload, verbose, debug))
    web_process.start()
    web_process.join()


@click.option(
    "-H",
    "--host",
    help="Host interface to listen on. Use 0.0.0.0 for all available interfaces.",
    type=click.STRING,
    default=settings.server.HOST,
    required=False,
    show_default=True,
)
@click.option(
    "-p",
    "--port",
    help="Port to bind.",
    type=click.INT,
    default=settings.server.PORT,
    required=False,
    show_default=True,
)
@click.option(
    "-W",
    "--http-workers",
    help="The number of HTTP worker processes for handling requests.",
    type=click.IntRange(min=1, max=multiprocessing.cpu_count() + 1),
    default=multiprocessing.cpu_count() + 1,
    required=False,
    show_default=True,
)
@click.option("-r", "--reload", help="Enable reload", is_flag=True, default=False, type=bool)
@click.option("-v", "--verbose", help="Enable verbose logging.", is_flag=True, default=False, type=bool)
@click.option("-d", "--debug", help="Enable debugging.", is_flag=True, default=False, type=bool)
@click.command(name="run-all", help="Starts the bot and the application server.")
def run_all(
    host: str,
    port: int | None,
    http_workers: int | None,
    reload: bool | None,
    verbose: bool | None,
    debug: bool | None,
) -> None:
    """Runs both the bot and the web server."""
    bot_process = multiprocessing.Process(target=bot)
    web_process = multiprocessing.Process(target=web, args=(host, port, http_workers, reload, verbose, debug))
    frontend_process = multiprocessing.Process(target=frontend)

    bot_process.start()
    web_process.start()
    frontend_process.start()

    bot_process.join()
    web_process.join()
    frontend_process.join()


def _convert_uvicorn_args(args: dict[str, Any]) -> list[str]:
    process_args: list[str] = []
    for arg, value in args.items():
        if isinstance(value, list):
            process_args.extend(f"--{arg}={val}" for val in value)
        if isinstance(value, bool):
            if value:
                process_args.append(f"--{arg}")
        else:
            process_args.append(f"--{arg}={value}")

    return process_args
