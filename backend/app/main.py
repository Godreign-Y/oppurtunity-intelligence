"""
Main entry point of the FastAPI application.
"""

from fastapi import FastAPI


def create_application() -> FastAPI:
    """
    Create and configure FastAPI app.

    Returns:
        FastAPI: application instance
    """
    app = FastAPI(
        title="Signal Intelligence Platform",
        debug=True,
    )

    return app


app = create_application()