"""Project Settings."""
from __future__ import annotations

import binascii
import os
from pathlib import Path
from typing import Any, Final, Literal

from dotenv import load_dotenv
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.data_extractors import RequestExtractorField, ResponseExtractorField  # noqa: TCH002
from pydantic import ValidationError, field_validator
from pydantic.types import SecretBytes
from pydantic_settings import BaseSettings, SettingsConfigDict

from src import utils
from src.__metadata__ import __version__ as version

__all__ = ()

load_dotenv()

DEFAULT_MODULE_NAME = "src"
BASE_DIR: Final = utils.module_to_os_path(DEFAULT_MODULE_NAME)
STATIC_DIR = Path(BASE_DIR / "server" / "domain" / "web" / "resources")
TEMPLATES_DIR = Path(BASE_DIR / "server" / "domain" / "web" / "templates")


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
    DESCRIPTION: str | None = """The Byte Bot API supports the Byte Discord bot.
                                  You can find out more about this project in the
                                  [docs](https://docs.byte-bot.app/latest)."""
    SERVERS: list[dict[str, str]] = []
    """Servers to use for the OpenAPI documentation."""
    EXTERNAL_DOCS: dict[str, str] | None = {
        "description": "Byte Bot API Docs",
        "url": "https://docs.byte-bot.app/latest",
    }
    """External documentation for the API."""

    @classmethod
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


class DatabaseSettings(BaseSettings):
    """Configures the database for the application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DB_",
        case_sensitive=False,
    )

    ECHO: bool = False
    """Enable SQLAlchemy engine logs."""
    ECHO_POOL: bool | Literal["debug"] = False
    """Enable SQLAlchemy connection pool logs."""
    POOL_DISABLE: bool = True
    """Disable SQLAlchemy pooling, same as setting pool to.

    See :class:`NullPool <sqlalchemy.pool.NullPool>`.
    """
    POOL_MAX_OVERFLOW: int = 10
    """See :class:`QueuePool <sqlalchemy.pool.QueuePool>`.

    .. warning:: This is arguably pretty high,
        and shouldn't be raised past 10.
    """
    POOL_SIZE: int = 5
    """See :class:`QueuePool <sqlalchemy.pool.QueuePool>`."""
    POOL_TIMEOUT: int = 30
    """See :class:`QueuePool <sqlalchemy.pool.QueuePool>`."""
    POOL_RECYCLE: int = 300
    """See :class:`QueuePool <sqlalchemy.pool.QueuePool>`."""
    POOL_PRE_PING: bool = False
    """See :class:`QueuePool <sqlalchemy.pool.QueuePool>`."""
    CONNECT_ARGS: dict[str, Any] = {}
    """Connection arguments to pass to the database driver."""
    URL: str = "postgresql+asyncpg://byte:bot@localhost:5432/byte"
    """Database connection URL."""
    ENGINE: str | None = None
    """Database engine."""
    USER: str = "byte"
    """Database user."""
    PASSWORD: str = "bot"
    """Database password."""
    HOST: str = "localhost"
    """Database host."""
    PORT: int = 5432
    """Database port."""
    NAME: str = "byte"
    """Database name."""
    MIGRATION_CONFIG: str = f"{BASE_DIR}/server/lib/db/alembic.ini"
    """Path to Alembic config file."""
    MIGRATION_PATH: str = f"{BASE_DIR}/server/lib/db/migrations"
    """Path to Alembic migration files."""
    MIGRATION_DDL_VERSION_TABLE: str = "ddl_version"
    """Name of the table used to track DDL version."""


# noinspection PyShadowingNames
def load_settings() -> (
    tuple[
        ProjectSettings, APISettings, OpenAPISettings, TemplateSettings, ServerSettings, LogSettings, DatabaseSettings
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
        project: ProjectSettings = ProjectSettings.model_validate({})
        api: APISettings = APISettings.model_validate({})
        openapi: OpenAPISettings = OpenAPISettings.model_validate({})
        template: TemplateSettings = TemplateSettings.model_validate({})
        log: LogSettings = LogSettings.model_validate({})
        database: DatabaseSettings = DatabaseSettings.model_validate({})

    except ValidationError as error:
        print(f"Could not load settings. Error: {error!r}")  # noqa: T201
        raise error from error
    return (
        project,
        api,
        openapi,
        template,
        server,
        log,
        database,
    )


(
    project,
    api,
    openapi,
    template,
    server,
    log,
    db,
) = load_settings()