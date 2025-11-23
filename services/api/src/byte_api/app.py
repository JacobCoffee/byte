"""ASGI application factory."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from litestar import Litestar

__all__ = ["create_app"]


def create_app() -> Litestar:
    """Application factory to instantiate a Litestar application.

    Returns:
        Litestar: The Litestar application.
    """
    from advanced_alchemy.exceptions import (
        RepositoryError as AdvancedAlchemyRepositoryError,
    )
    from litestar import Litestar
    from pydantic import SecretStr

    from byte_api import domain
    from byte_api.lib import (
        cors,
        db,
        exceptions,
        log,
        openapi,
        schema,
        settings,
        static_files,
        template,
    )
    from byte_api.lib.dependencies import create_collection_dependencies

    dependencies = create_collection_dependencies()

    return Litestar(
        # Handlers
        exception_handlers={
            exceptions.ApplicationError: exceptions.exception_to_http_response,
            AdvancedAlchemyRepositoryError: exceptions.exception_to_http_response,
        },
        route_handlers=[*domain.routes],
        # Configs
        cors_config=cors.config,
        logging_config=log.config,
        openapi_config=openapi.config,
        static_files_config=static_files.config,
        template_config=template.config,
        dependencies=dependencies,
        # Lifecycle
        before_send=[log.controller.BeforeSendHandler()],
        on_shutdown=[],
        on_startup=[lambda: log.configure(log.default_processors)],  # type: ignore[arg-type]
        on_app_init=[],
        # Other
        debug=settings.project.DEBUG,
        middleware=[log.controller.middleware_factory],
        signature_namespace=domain.signature_namespace,
        type_encoders={
            SecretStr: str,
            schema.CamelizedBaseModel: schema.serialize_camelized_model,
        },
        plugins=[db.plugin],
    )


def create_bot() -> None:
    """Application factory to instantiate a Discord bot.

    .. todo:: Move into this file.
    """


app = create_app()
bot = create_bot()
