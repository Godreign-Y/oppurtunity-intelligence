"""Persistence repository for final business intelligence."""

from sqlalchemy.ext.asyncio import AsyncSession

from redit.aggregation.models import FinalIntelligence
from redit.storage.models import FinalBusinessIntelligenceORM
from redit.utils.logging import get_logger

logger = get_logger(__name__)


class AggregationRepository:
    """Store final business intelligence records."""

    async def store_intelligence(
        self,
        db: AsyncSession,
        records: list[FinalIntelligence],
    ) -> None:
        """Persist final business intelligence records."""

        logger.info(
            "Storing final business intelligence",
            extra={"count": len(records)},
        )

        for record in records:
            orm_record = FinalBusinessIntelligenceORM(
                id=record.id,
                cluster_theme=record.cluster_theme,
                problem_statement=record.problem_statement,
                precise_description_of_the_problem=record.precise_description_of_the_problem,
                supporting_post_count=record.supporting_post_count,
                business_score=record.business_score,
                avg_frustration_score=record.avg_frustration_score,
                affected_tools=record.affected_tools,
                possible_companies_affected=record.possible_companies_affected,
            )
            db.add(orm_record)

        await db.commit()

        logger.info("Final business intelligence persisted successfully")
