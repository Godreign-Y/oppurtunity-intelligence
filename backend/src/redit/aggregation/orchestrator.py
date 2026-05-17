"""Aggregation orchestrator: cluster analysis → final business intelligence."""

from sqlalchemy.ext.asyncio import AsyncSession

from redit.aggregation.models import FinalIntelligence
from redit.aggregation.repository import AggregationRepository
from redit.aggregation.service import AggregationService
from redit.clustering.orchestrator import ClusteringOrchestrator
from redit.utils.logging import get_logger

logger = get_logger(__name__)


class AggregationOrchestrator:
    """End-to-end: clustering → aggregation → persistence."""

    def __init__(self) -> None:
        """Initialize sub-orchestrators and services."""
        self.clustering_orchestrator = ClusteringOrchestrator()
        self.aggregation_service = AggregationService()
        self.aggregation_repository = AggregationRepository()

    async def run(
        self,
        db: AsyncSession,
    ) -> dict:
        """
        Execute full aggregation pipeline.

        Steps:
        1. Run in-memory clustering
        2. Enrich clusters with metadata
        3. Aggregate to final business intelligence
        4. Persist to database

        Returns:
            dict with aggregation stats
        """
        logger.info("Starting aggregation pipeline")

        cluster_analyses = await (
            self.clustering_orchestrator.run_and_analyze(db)
        )

        if len(cluster_analyses) == 0:
            logger.info("No clusters found; skipping aggregation")
            return {
                "status": "no_clusters",
                "final_intelligence_records": 0,
            }

        await self.clustering_orchestrator.fetch_cluster_metadata(
            db,
            cluster_analyses,
        )

        max_cluster_size = max(
            (len(a.record_ids) for a in cluster_analyses.values()),
            default=1,
        )

        final_intelligence = (
            self.aggregation_service.aggregate_clusters(
                cluster_analyses,
                max_cluster_size,
            )
        )

        await self.aggregation_repository.store_intelligence(
            db,
            final_intelligence,
        )

        logger.info(
            "Aggregation pipeline complete",
            extra={"final_records": len(final_intelligence)},
        )

        return {
            "status": "success",
            "clusters_analyzed": len(cluster_analyses),
            "final_intelligence_records": len(final_intelligence),
        }
