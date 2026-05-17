"""Aggregation service for converting clusters to business intelligence."""

from collections import Counter
from uuid import uuid4

import numpy as np

from redit.aggregation.models import (
    ClusterAnalysis,
    FinalIntelligence,
)
from redit.utils.logging import get_logger

logger = get_logger(__name__)


class AggregationService:
    """Convert in-memory semantic clusters to final business intelligence."""

    def aggregate_clusters(
        self,
        cluster_analyses: dict[int, ClusterAnalysis],
        max_cluster_size: int,
    ) -> list[FinalIntelligence]:
        """
        Transform cluster analyses into final business intelligence records.

        Args:
            cluster_analyses:
                dict mapping cluster_id -> ClusterAnalysis

            max_cluster_size:
                largest cluster size (for normalization)

        Returns:
            list of FinalIntelligence records
        """

        logger.info(
            "Aggregating clusters to business intelligence",
            extra={"cluster_count": len(cluster_analyses)},
        )

        final_records: list[FinalIntelligence] = []

        for cluster_id, analysis in cluster_analyses.items():

            if len(analysis.record_ids) == 0:
                logger.warning(
                    "Skipping empty cluster",
                    extra={"cluster_id": cluster_id},
                )
                continue

            intelligence = self._aggregate_single_cluster(
                cluster_id,
                analysis,
                max_cluster_size,
            )

            final_records.append(intelligence)

        logger.info(
            "Aggregation complete",
            extra={"final_records": len(final_records)},
        )

        return final_records

    def _aggregate_single_cluster(
        self,
        cluster_id: int,
        analysis: ClusterAnalysis,
        max_cluster_size: int,
    ) -> FinalIntelligence:
        """Aggregate a single cluster into business intelligence."""

        cluster_size = len(analysis.record_ids)

        avg_frustration = (
            float(np.mean(analysis.frustration_scores))
            if analysis.frustration_scores
            else 0.0
        )

        avg_relevance = (
            float(np.mean(analysis.business_relevance_scores))
            if analysis.business_relevance_scores
            else 0.0
        )

        business_score = self._calculate_business_score(
            avg_relevance,
            avg_frustration,
            cluster_size,
            max_cluster_size,
        )

        representative_problem = (
            self._select_representative_problem(
                analysis.problem_statements
            )
        )

        affected_tools = self._deduplicate_list(
            [
                tool
                for tools_list in analysis.affected_tools_list
                for tool in tools_list
            ]
        )

        companies = self._deduplicate_list(
            [
                company
                for companies_list in analysis.companies_list
                for company in companies_list
            ]
        )

        precise_desc = self._generate_precise_description(
            representative_problem,
            cluster_size,
            avg_frustration,
        )

        return FinalIntelligence(
            id=uuid4(),
            cluster_theme=representative_problem,
            problem_statement=representative_problem,
            precise_description_of_the_problem=precise_desc,
            supporting_post_count=cluster_size,
            business_score=business_score,
            avg_frustration_score=avg_frustration,
            affected_tools=affected_tools,
            possible_companies_affected=companies,
        )

    def _select_representative_problem(
        self,
        problem_statements: list[str],
    ) -> str:
        """
        Select stable representative problem statement.

        Uses most frequent canonical statement instead of
        arbitrary first cluster member.
        """

        if not problem_statements:
            return "Unclassified workflow pain"

        counter = Counter(problem_statements)

        return counter.most_common(1)[0][0]

    def _calculate_business_score(
        self,
        avg_relevance: float,
        avg_frustration: float,
        cluster_size: int,
        max_cluster_size: int,
    ) -> float:
        """
        Calculate business score using weighted formula.

        Formula:
        (
            avg_relevance * 0.5
            + avg_frustration * 0.3
            + normalized_size * 0.2
        ) * 10
        """

        normalized_size = (
            cluster_size / max(max_cluster_size, 1)
        )

        score = (
            avg_relevance * 0.5
            + avg_frustration * 0.3
            + normalized_size * 0.2
        ) * 10.0

        return min(10.0, max(0.0, score))

    def _deduplicate_list(
        self,
        items: list[str],
    ) -> list[str]:
        """Deduplicate and sort list."""

        return sorted(list(set(items)))

    def _generate_precise_description(
        self,
        problem_statement: str,
        cluster_size: int,
        avg_frustration: float,
    ) -> str:
        """Generate concise business-facing description."""

        frustration_level = (
            "severe"
            if avg_frustration > 0.75
            else (
                "significant"
                if avg_frustration > 0.5
                else "moderate"
            )
        )

        return (
            f"{problem_statement} "
            f"({cluster_size} incidents, "
            f"{frustration_level} impact)"
        )