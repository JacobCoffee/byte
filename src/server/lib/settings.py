"""Project Settings."""
from __future__ import annotations

import binascii
import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.data_extractors import RequestExtractorField, ResponseExtractorField  # noqa: TCH002
from pydantic import ValidationError, field_validator
from pydantic.types import SecretBytes, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from src import utils
from src.__metadata__ import __version__ as version

__all__ = ()

load_dotenv()

DEFAULT_MODULE_NAME = "src"
BASE_DIR: Final = utils.module_to_os_path(DEFAULT_MODULE_NAME)
STATIC_DIR = Path(BASE_DIR / "server" / "domain" / "web" / "resources")
TEMPLATES_DIR = Path(BASE_DIR / "server" / "domain" / "web" / "templates")
COMMANDS_DIR = utils.module_to_os_path("src.byte.commands")


class DiscordSettings(BaseSettings):
    """Discord Settings."""

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_prefix="DISCORD_")

    API_TOKEN: SecretStr
    """Discord API token."""
    COMMAND_PREFIX: str = "!"
    """Command prefix for bot commands."""
    DEV_GUILD_ID: int
    """Discord Guild ID for development."""
    DEV_USER_ID: int
    """Discord User ID for development."""
    COMMANDS_LOC: str = "src.byte.commands"
    """Base Path to commands directory."""
    COMMANDS_DIRS: list[str] = [f"{COMMANDS_DIR}"]
    """Directories to search for commands."""


class ServerSettings(BaseSettings):
    """Server configurations."""

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_prefix="SERVER_")

    APP_LOC: str = "src.app:create_app"
    """Path to app executable, or factory."""
    APP_LOC_IS_FACTORY: bool = True
    """Indicate if APP_LOC points to an executable or factory."""
    HOST: str = "localhost"
    """Server network host."""
    KEEPALIVE: int = 65
    """Seconds to hold connections open."""
    PORT: int = 8000
    """Server port."""
    RELOAD: bool | None = False
    """Turn on hot reloading."""
    RELOAD_DIRS: list[str] = [f"{BASE_DIR}"]
    """Directories to watch for reloading.

    .. warning:: This only accepts a single directory for now, something is broken

    """
    HTTP_WORKERS: int | None = None
    """Number of HTTP Worker processes to be spawned by Uvicorn."""


class ProjectSettings(BaseSettings):
    """Project Settings."""

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="allow")

    BUILD_NUMBER: str = ""
    """Identifier for CI build."""
    CHECK_DB_READY: bool = True
    """Check for database readiness on startup."""
    CHECK_REDIS_READY: bool = True
    """Check for redis readiness on startup."""
    DEBUG: bool = False
    """Run ``Litestar`` with ``debug=True``."""
    ENVIRONMENT: str = "prod"
    """``dev``, ``prod``, ``qa``, etc."""
    TEST_ENVIRONMENT_NAME: str = "test"
    """Value of ENVIRONMENT used to determine if running tests.

    This should be the value of ``ENVIRONMENT`` in ``tests.env``.
    """
    LOCAL_ENVIRONMENT_NAME: str = "local"
    """Value of ENVIRONMENT used to determine if running in local development
    mode.

    This should be the value of ``ENVIRONMENT`` in your local ``.env`` file.
    """
    NAME: str = "Byte Bot"
    """Application name."""
    SECRET_KEY: SecretBytes
    """Secret key used for signing cookies and other things."""
    JWT_ENCRYPTION_ALGORITHM: str = "HS256"
    """Algorithm used to encrypt JWTs."""
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    """List of origins allowed to access the API."""
    STATIC_URL: str = "/static/"
    """Default URL where static assets are located."""
    CSRF_COOKIE_NAME: str = "csrftoken"
    """Name of the CSRF cookie."""
    CSRF_COOKIE_SECURE: bool = False
    """Set the CSRF cookie to be secure."""
    STATIC_DIR: Path = STATIC_DIR
    """Path to static assets."""
    DEV_MODE: bool = False
    """Indicate if running in development mode."""

    @property
    def slug(self) -> str:
        """Return a slugified name.

        Returns:
            ``self.NAME``, all lowercase and hyphens instead of spaces.
        """
        return "-".join(s.lower() for s in self.NAME.split())

    @classmethod
    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(
        cls,
        value: str | list[str] | None,
    ) -> list[str] | str:
        """Parse a list of origins.

        Args:
            value: A comma-separated string of origins, or a list of origins.

        Returns:
            A list of origins.

        Raises:
            ValueError: If ``value`` is not a list or string.
        """
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str) and not value.startswith("["):
            return [host.strip() for host in value.split(",")]
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            return list(value)
        raise ValueError(value)

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def generate_secret_key(cls, value: str | None) -> SecretBytes:
        """Generate a secret key.

        Args:
            value: A secret key, or ``None``.

        Returns:
            A secret key.
        """
        if value is None:
            return SecretBytes(binascii.hexlify(os.urandom(32)))
        return SecretBytes(value.encode())


class APISettings(BaseSettings):
    """API specific configuration."""

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_prefix="API_")

    HEALTH_PATH: str = "/health"
    """Route that the health check is served under."""


class LogSettings(BaseSettings):
    """Logging config for the Project."""

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_prefix="LOG_")

    """https://stackoverflow.com/a/1845097/6560549"""
    EXCLUDE_PATHS: str = r"\A(?!x)x"
    """Regex to exclude paths from logging."""
    HTTP_EVENT: str = "HTTP"
    """Log event name for logs from ``litestar`` handlers."""
    INCLUDE_COMPRESSED_BODY: bool = False
    """Include ``body`` of compressed responses in log output."""
    LEVEL: int = 20
    """Stdlib log levels.

    Only emit logs at this level, or higher.
    """
    OBFUSCATE_COOKIES: set[str] = {"session"}
    """Request cookie keys to obfuscate."""
    OBFUSCATE_HEADERS: set[str] = {"Authorization", "X-API-KEY"}
    """Request header keys to obfuscate."""
    JOB_FIELDS: list[str] = [
        "function",
        "kwargs",
        "key",
        "scheduled",
        "attempts",
        "completed",
        "queued",
        "started",
        "result",
        "error",
    ]
    """Attributes of the SAQ :class:`Job <saq.job.Job>` to be logged."""
    REQUEST_FIELDS: list[RequestExtractorField] = [
        "path",
        "method",
        "headers",
        "cookies",
        "query",
        "path_params",
        "body",
    ]
    """Attributes of the :class:`Request <litestar.connection.request.Request>` to be
    logged."""
    RESPONSE_FIELDS: list[ResponseExtractorField] = [
        "status_code",
        "cookies",
        "headers",
        # "body",  # ! We don't want to log the response body.
    ]
    """Attributes of the :class:`Response <litestar.response.Response>` to be
    logged."""
    UVICORN_ACCESS_LEVEL: int = 30
    """Level to log uvicorn access logs."""
    UVICORN_ERROR_LEVEL: int = 20
    """Level to log uvicorn error logs."""


# noinspection PyUnresolvedReferences
class OpenAPISettings(BaseSettings):
    """Configures OpenAPI for the Project."""

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_prefix="OPENAPI_")

    CONTACT_NAME: str = "Admin"
    """Name of contact on document."""
    CONTACT_EMAIL: str = "hello@byte-bot.app"
    """Email for contact on document."""
    TITLE: str | None = "Byte Bot"
    """Document title."""
    VERSION: str = version
    """Document version."""
    PATH: str = "/api"
    """Path to access the root API documentation."""
    DESCRIPTION: str | None = f"""The Byte Bot API supports the Byte Discord bot.
                                  You can find out more about this project in the
                                  [docs]({os.getenv("WEB_URL", "http://localhost") + "docs"})."""
    SERVERS: list[dict[str, str]] = []
    """Servers to use for the OpenAPI documentation."""
    EXTERNAL_DOCS: dict[str, str] | None = {
        "description": "Byte Bot API Docs",
        "url": os.getenv("WEB_URL", "http://localhost") + "docs",
    }
    """External documentation for the API."""

    @classmethod  # pyright: ignore
    @field_validator("SERVERS", mode="before")
    def assemble_openapi_servers(cls, value: list[dict[str, str]]) -> list[dict[str, str]]:
        """Assembles the OpenAPI servers based on the environment.

        Args:
            value: The value of the SERVERS setting.

        Returns:
            The assembled OpenAPI servers.
        """
        env_urls = {
            "prod": "https://byte-bot.app/",
            "test": "https://dev.byte-bot.app/",
            "dev": "http://0.0.0.0:8000",
        }
        environment = os.getenv("ENVIRONMENT", "dev")
        url = os.getenv("WEB_URL", env_urls[environment])
        description = environment.capitalize()

        return [
            {
                "url": url,  # type: ignore[list-item]
                "description": f"{description}",
            }
            if environment in env_urls
            else value
        ]


class TemplateSettings(BaseSettings):
    """Configures Templating for the project."""

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_prefix="TEMPLATE_")

    ENGINE: type[JinjaTemplateEngine] = JinjaTemplateEngine
    """Template engine to use. (Jinja2 or Mako)"""


class HTTPClientSettings(BaseSettings):
    """HTTP Client configurations."""

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_prefix="HTTP_")

    BACKOFF_MAX: float = 60
    BACKOFF_MIN: float = 0
    EXPONENTIAL_BACKOFF_BASE: float = 2
    EXPONENTIAL_BACKOFF_MULTIPLIER: float = 1


# noinspection PyShadowingNames
def load_settings() -> (
    tuple[
        DiscordSettings,
        ProjectSettings,
        APISettings,
        OpenAPISettings,
        TemplateSettings,
        ServerSettings,
        LogSettings,
        HTTPClientSettings,
    ]
):
    """Load Settings file.

    Returns:
        Settings: application settings
    """
    try:
        """Override Application reload dir."""

        server: ServerSettings = ServerSettings.model_validate(
            {"HOST": "0.0.0.0", "RELOAD_DIRS": [str(BASE_DIR)]},  # noqa: S104
        )
        discord: DiscordSettings = DiscordSettings.model_validate({})
        project: ProjectSettings = ProjectSettings.model_validate({})
        api: APISettings = APISettings.model_validate({})
        openapi: OpenAPISettings = OpenAPISettings.model_validate({})
        template: TemplateSettings = TemplateSettings.model_validate({})
        log: LogSettings = LogSettings.model_validate({})
        http_client: HTTPClientSettings = HTTPClientSettings.model_validate({})

    except ValidationError as error:
        print(f"Could not load settings. Error: {error!r}")  # noqa: T201
        raise error from error
    return (
        discord,
        project,
        api,
        openapi,
        template,
        server,
        log,
        http_client,
    )


(
    discord,
    project,
    api,
    openapi,
    template,
    server,
    log,
    http_client,
) = load_settings()
