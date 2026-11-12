from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

import app.models  # noqa: F401
from app.api.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import engine


logger = logging.getLogger(__name__)


def create_app(*, init_db: bool = True) -> FastAPI:
    """Create the FastAPI app. Tests call this with init_db=False."""

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        """Run code when the app starts and when it stops."""

        configure_logging()

        logger.info("Starting %s", settings.APP_NAME)

        if init_db:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables initialized successfully")

        yield

        logger.info("Shutting down %s", settings.APP_NAME)

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        openapi_tags=[
            {
                "name": "Addresses",
                "description": "Create, retrieve, update, delete, and search address records.",
            },
            {
                "name": "Health",
                "description": "Application status and database readiness.",
            },
        ],
        lifespan=lifespan,
    )

    register_exception_handlers(application)
    application.include_router(health_router)
    application.include_router(api_router, prefix="/api/v1")

    return application


app = create_app()
