from fastapi import FastAPI
from app.core.middleware import ApiLoggingMiddleware
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.config import settings
from app.core.exceptions import (
    SaaSForgeError,
    generic_exception_handler,
    saasforge_exception_handler,
)
from app.core.logging import setup_logging


import sentry_sdk
from prometheus_fastapi_instrumentator import Instrumentator

def create_app() -> FastAPI:
    # Set up structured logging
    setup_logging(json_logs=settings.ENVIRONMENT != "local")
    
    # Initialize Sentry
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            traces_sample_rate=1.0,
        )


    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # Initialize Prometheus Instrumentator
    Instrumentator().instrument(app).expose(app, include_in_schema=False, should_gzip=True)


    # CORS Configuration
    app.add_middleware(ApiLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,  # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    app.add_exception_handler(SaaSForgeError, saasforge_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, generic_exception_handler)

    # Routers
    app.include_router(router, prefix=settings.API_V1_STR)

    # Root redirect or health is often useful at /
    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

    return app


app = create_app()
