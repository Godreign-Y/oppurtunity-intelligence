"""Aggregation domain models."""

from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class ClusterAnalysis:
    """In-memory cluster analysis before aggregation."""

    cluster_id: int
    record_ids: list[UUID] = field(default_factory=list)
    problem_statements: list[str] = field(default_factory=list)
    frustration_scores: list[float] = field(default_factory=list)
    business_relevance_scores: list[float] = field(default_factory=list)
    affected_tools_list: list[list[str]] = field(default_factory=list)
    companies_list: list[list[str]] = field(default_factory=list)


@dataclass
class FinalIntelligence:
    """Final aggregated business intelligence for a cluster."""

    id: UUID | None = None
    cluster_theme: str = ""
    problem_statement: str = ""
    precise_description_of_the_problem: str = ""
    supporting_post_count: int = 0
    business_score: float = 0.0
    avg_frustration_score: float = 0.0
    affected_tools: list[str] = field(default_factory=list)
    possible_companies_affected: list[str] = field(default_factory=list)
