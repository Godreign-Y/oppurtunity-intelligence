"""Clustering pipeline orchestrator."""

import asyncio

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from redit.aggregation.models import ClusterAnalysis
from redit.clustering.repository import ClusteringRepository
from redit.clustering.service import (
    SemanticClusteringService,
)
from redit.utils.logging import get_logger

logger = get_logger(__name__)


class ClusteringOrchestrator:
    """
    Semantic clustering:
    UMAP + HDBSCAN.

    Returns in-memory cluster analysis.
    """

    def __init__(self) -> None:

        self.clustering_service = (
            SemanticClusteringService()
        )

        self.repository = (
            ClusteringRepository()
        )

    async def run_and_analyze(
        self,
        db: AsyncSession,
    ) -> dict[int, ClusterAnalysis]:
        """
        Execute clustering pipeline.

        CPU-heavy clustering work is moved
        off the main async event loop.
        """

        logger.info(
            "Starting clustering pipeline"
        )

        records = (
            await self.repository.fetch_all_records(
                db
            )
        )

        logger.info(
            "Fetched records for clustering",
            extra={
                "count": len(records)
            },
        )

        if len(records) == 0:

            logger.warning(
                "No records found"
            )

            return {}

        if len(records) < 5:

            logger.warning(
                "Insufficient records for clustering",
                extra={
                    "count": len(records)
                },
            )

            return {}

        record_ids = [
            r[0]
            for r in records
        ]

        problem_statements = [
            r[1]
            for r in records
        ]

        embeddings_list = [
            r[2]
            for r in records
        ]

        embeddings = np.array(
            embeddings_list,
            dtype=np.float32,
        )

        # -----------------------------------
        # OFFLOAD CPU-HEAVY CLUSTERING
        # TO BACKGROUND THREAD
        # -----------------------------------

        reduced_embeddings, labels = (
            await asyncio.to_thread(
                self.clustering_service.fit_and_predict,
                embeddings,
            )
        )

        cluster_assignments = (
            self.clustering_service.get_cluster_assignments(
                labels
            )
        )

        logger.info(
            "Generated cluster assignments",
            extra={
                "n_clusters":
                    len(cluster_assignments)
            },
        )

        cluster_analyses: dict[
            int,
            ClusterAnalysis,
        ] = {}

        for cluster_id, indices in (
            cluster_assignments.items()
        ):

            analysis = ClusterAnalysis(
                cluster_id=cluster_id
            )

            for idx in indices:

                analysis.record_ids.append(
                    record_ids[idx]
                )

                analysis.problem_statements.append(
                    problem_statements[idx]
                )

            cluster_analyses[
                cluster_id
            ] = analysis

        logger.info(
            "Cluster analysis complete",
            extra={
                "clusters":
                    len(cluster_analyses)
            },
        )

        return cluster_analyses

    async def fetch_cluster_metadata(
        self,
        db: AsyncSession,
        cluster_analyses: dict[
            int,
            ClusterAnalysis,
        ],
    ) -> None:
        """
        Enrich cluster analyses with metadata.
        """

        logger.info(
            "Enriching cluster metadata"
        )

        from sqlalchemy import select

        from redit.storage.models import (
            CanonicalIntelligenceORM,
        )

        relevant_ids = []

        for analysis in (
            cluster_analyses.values()
        ):

            relevant_ids.extend(
                analysis.record_ids
            )

        relevant_ids = list(
            set(relevant_ids)
        )

        if not relevant_ids:

            logger.warning(
                "No relevant IDs found"
            )

            return

        query = (
            select(
                CanonicalIntelligenceORM.id,
                CanonicalIntelligenceORM.frustration_score,
                CanonicalIntelligenceORM.business_relevance,
                CanonicalIntelligenceORM.affected_tools,
                CanonicalIntelligenceORM.possible_companies_affected,
            )
            .where(
                CanonicalIntelligenceORM.id.in_(
                    relevant_ids
                )
            )
        )

        result = await db.execute(query)

        records_by_id = {
            r[0]: r
            for r in result.fetchall()
        }

        for analysis in (
            cluster_analyses.values()
        ):

            for record_id in (
                analysis.record_ids
            ):

                if (
                    record_id
                    not in records_by_id
                ):
                    continue

                rec = records_by_id[
                    record_id
                ]

                analysis.frustration_scores.append(
                    rec[1]
                )

                analysis.business_relevance_scores.append(
                    rec[2]
                )

                analysis.affected_tools_list.append(
                    rec[3] or []
                )

                analysis.companies_list.append(
                    rec[4] or []
                )

        logger.info(
            "Metadata enrichment complete"
        )