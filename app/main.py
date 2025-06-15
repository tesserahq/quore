import logging
from app.middleware.db_session import DBSessionMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
import rollbar
from rollbar.logger import RollbarHandler

from .routers import (
    workspace,
    user,
    membership,
    project,
    ingest,
    llm,
    plugin,
    credential,
    system,
)
from .routers.assistant import assistant_router
from .ws import status
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.telemetry import setup_tracing
from app.exceptions.handlers import register_exception_handlers
from app.core.logging_config import get_logger
from app.plugins.datetime import plugin_app as datetime_plugin


def create_app(testing: bool = False, auth_middleware=None) -> FastAPI:
    logger = get_logger()
    settings = get_settings()

    if settings.is_production:
        # Initialize Rollbar SDK with your server-side access token
        rollbar.init(
            settings.rollbar_access_token,
            environment=settings.environment,
            handler="async",
        )

        # Report ERROR and above to Rollbar
        rollbar_handler = RollbarHandler()
        rollbar_handler.setLevel(logging.ERROR)

        # Attach Rollbar handler to the root logger
        logger.addHandler(rollbar_handler)

    # Create the ASGI app
    mcp_app = datetime_plugin.http_app(path="/mcp")
    lifespan = mcp_app.lifespan

    app = FastAPI(lifespan=lifespan)

    if not testing and not settings.disable_auth:
        logger.info("Main: Adding authentication middleware")
        from app.middleware.authentication import AuthenticationMiddleware

        app.add_middleware(AuthenticationMiddleware)
    else:
        logger.info("Main: No authentication middleware")
        if auth_middleware:
            app.add_middleware(auth_middleware)

    app.add_middleware(DBSessionMiddleware)

    # TODO: Restrict this to the allowed origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Puedes restringir esto a dominios específicos
        allow_credentials=True,
        allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
        allow_headers=["*"],  # Permitir todos los headers
    )

    app.include_router(workspace.router)
    app.include_router(user.router)
    app.include_router(membership.router)
    app.include_router(project.router)
    app.include_router(ingest.router)
    app.include_router(status.router)
    app.include_router(llm.router)
    app.include_router(plugin.router)
    app.include_router(credential.workspace_router)
    app.include_router(credential.credential_router)
    app.include_router(assistant_router())
    app.include_router(system.router)

    register_exception_handlers(app)

    # Mount sub-applications: /system/plugins/datetime/mcp
    app.mount("/system/plugins/datetime", mcp_app)

    return app


# Production app instance
app = create_app()

settings = get_settings()
if settings.otel_enabled:
    tracer_provider = setup_tracing()  # Or use env/config
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)


@app.get("/")
def main_route():
    return {"message": "Hey, It is me Goku"}
