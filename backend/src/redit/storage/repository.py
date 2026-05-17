"""Persistence repository for canonical intelligence."""

import asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from redit.embeddings.service import EmbeddingService
from redit.models.intelligence import IntelligenceRecord
from redit.storage.models import CanonicalIntelligenceORM


class CanonicalIntelligenceRepository:
    """Store canonical intelligence + embeddings."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
    ) -> None:

        self.embedding_service = embedding_service

    async def store_record(
        self,
        db: AsyncSession,
        record: IntelligenceRecord,
    ) -> None:
        """
        Persist intelligence record with embedding.

        IMPORTANT:
        - Embedding generation runs in background thread
        - Prevents asyncio event loop blocking
        - Prevents Neon asyncpg disconnects
        - Uses flush() instead of commit()
        """

        # -----------------------------------------
        # OFFLOAD CPU-HEAVY EMBEDDING GENERATION
        # TO BACKGROUND THREAD
        # -----------------------------------------

        embedding = await asyncio.to_thread(
            self.embedding_service.generate_embedding,
            problem_statement=record.problem_statement,
            pain_category=record.pain_category,
        )

        db_record = CanonicalIntelligenceORM(
            id=uuid4(),
            post_id=record.post_id,
            problem_statement=record.problem_statement,
            pain_category=record.pain_category,
            business_impact=record.business_impact,
            frustration_score=record.frustration_score,
            business_relevance=record.business_relevance,
            affected_tools=record.affected_tools,
            affected_platforms=record.affected_platforms,
            possible_companies_affected=(
                record.possible_companies_affected
            ),
            embedding=embedding,
        )

        db.add(db_record)

        # Flush sends INSERT without ending transaction.
        # Keeps transaction alive without commit churn.
        await db.flush()

    async def commit(
        self,
        db: AsyncSession,
    ) -> None:
        """
        Commit ingestion batch transaction.
        """

        await db.commit()

    async def rollback(
        self,
        db: AsyncSession,
    ) -> None:
        """
        Rollback failed ingestion transaction.
        """

        await db.rollback()