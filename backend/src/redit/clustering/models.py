"""Clustering domain models."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ClusterMetadata:
    """Cluster semantic metadata."""

    cluster_id: int
    cluster_theme: str
    representative_problem_statement: str
    cluster_size: int
    created_at: datetime | None = None


@dataclass
class ClusterMembership:
    """Record-to-cluster membership."""

    id: UUID | None = None
    canonical_record_id: UUID | None = None
    cluster_id: int | None = None
    distance_score: float | None = None
    created_at: datetime | None = None
