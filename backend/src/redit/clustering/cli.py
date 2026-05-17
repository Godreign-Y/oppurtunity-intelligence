"""CLI for running clustering pipeline."""

import asyncio

from dotenv import load_dotenv

from redit.clustering.orchestrator import (
    ClusteringOrchestrator,
)
from redit.storage.database import (
    AsyncSessionLocal,
)
from redit.utils.logging import (
    configure_logging,
    get_logger,
)

load_dotenv()

logger = get_logger(__name__)


async def run_clustering() -> None:
    """
    Execute clustering pipeline
    on stored embeddings.
    """

    configure_logging("INFO")

    logger.info(
        "Starting clustering pipeline"
    )

    orchestrator = (
        ClusteringOrchestrator()
    )

    async with AsyncSessionLocal() as session:

        result = (
            await orchestrator.run_and_analyze(
                session
            )
        )

        logger.info(
            "Clustering pipeline complete",
            extra={
                "clusters": len(result)
            },
        )

        print(
            f"\n✓ Clustering complete: "
            f"{len(result)} clusters\n"
        )


if __name__ == "__main__":

    asyncio.run(run_clustering())