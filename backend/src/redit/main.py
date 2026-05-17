"""FastAPI application entrypoint."""

from dotenv import load_dotenv
load_dotenv()

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redit.api.router import api_router
from redit.config.settings import get_settings
from redit.ml.registry import ModelRegistry
from redit.storage.memory import InMemoryRunStore
from redit.utils.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize app state, load ML models, release on shutdown."""
    settings = get_settings()
    configure_logging(settings.log_level)
    app.state.run_store = InMemoryRunStore()
    app.state.models = ModelRegistry(settings)
    app.state.models.load()
    logger.info(
        "REDIT API started",
        extra={"env": settings.app_env, "reddit_source": settings.reddit_source},
    )
    yield
    app.state.models.unload()
    logger.info("REDIT API shutdown")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="Global Reddit discovery → ML filters → intelligence JSON",
        version="0.3.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()


def run() -> None:
    """CLI entrypoint for uvicorn."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "redit.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app_env == "development",
    )


if __name__ == "__main__":
    run()
