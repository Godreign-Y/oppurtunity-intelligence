"""Clustering persistence repository."""

from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from redit.clustering.models import (
    ClusterMembership,
    ClusterMetadata,
)
from redit.storage.models import (
    CanonicalIntelligenceORM,
    ClusterMembershipORM,
    PainClusterORM,
)
from redit.utils.logging import get_logger

logger = get_logger(__name__)


class ClusteringRepository:
    """Store and retrieve cluster metadata and memberships."""

    async def fetch_all_records(
        self,
        db: AsyncSession,
    ):
        """
        Fetch all canonical records with embeddings.

        Returns:
            list of:
            (id, problem_statement, embedding)
        """

        query = (
            select(
                CanonicalIntelligenceORM.id,
                CanonicalIntelligenceORM.problem_statement,
                CanonicalIntelligenceORM.embedding,
            )
            .where(
                CanonicalIntelligenceORM.embedding.is_not(None)
            )
        )

        result = await db.execute(query)

        return list(result.fetchall())

    async def clear_existing_clusters(
        self,
        db: AsyncSession,
    ) -> None:
        """Clear all existing cluster data for fresh reclustering."""

        logger.info("Clearing existing cluster data")

        await db.execute(delete(ClusterMembershipORM))
        await db.execute(delete(PainClusterORM))

        await db.commit()

    async def store_clusters(
        self,
        db: AsyncSession,
        clusters: dict[int, ClusterMetadata],
        memberships: list[ClusterMembership],
    ) -> None:
        """
        Persist cluster metadata and memberships.

        Args:
            db: async database session
            clusters: dict mapping cluster_id -> ClusterMetadata
            memberships: list of ClusterMembership records
        """

        logger.info(
            "Storing cluster data",
            extra={
                "n_clusters": len(clusters),
                "n_memberships": len(memberships),
            },
        )

        for cluster_id, metadata in clusters.items():
            orm_record = PainClusterORM(
                cluster_id=cluster_id,
                cluster_theme=metadata.cluster_theme,
                representative_problem_statement=(
                    metadata.representative_problem_statement
                ),
                cluster_size=metadata.cluster_size,
            )

            db.add(orm_record)

        for membership in memberships:
            orm_membership = ClusterMembershipORM(
                id=membership.id or uuid4(),
                canonical_record_id=membership.canonical_record_id,
                cluster_id=membership.cluster_id,
                distance_score=membership.distance_score,
            )

            db.add(orm_membership)

        await db.commit()

        logger.info(
            "Cluster data persisted successfully"
        )

    async def get_cluster_stats(
        self,
        db: AsyncSession,
    ) -> dict:
        """Get cluster statistics."""

        cluster_count = await db.execute(
            select(PainClusterORM)
        )

        clusters = cluster_count.scalars().all()

        membership_count = await db.execute(
            select(ClusterMembershipORM)
        )

        memberships = membership_count.scalars().all()

        return {
            "total_clusters": len(clusters),
            "total_memberships": len(memberships),
        }