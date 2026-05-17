"""SQLAlchemy storage models."""

from sqlalchemy import Float, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    """Base declarative class."""


class CanonicalIntelligenceORM(Base):
    """Persistent canonical intelligence record."""

    __tablename__ = "canonical_intelligence"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    post_id: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )

    problem_statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    pain_category: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    business_impact: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    frustration_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    business_relevance: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    affected_tools: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
    )

    affected_platforms: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
    )

    possible_companies_affected: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
    )

    embedding: Mapped[list[float]] = mapped_column(
        Vector(384),
        nullable=False,
    )

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )


class PainClusterORM(Base):
    """Semantic cluster of recurring workflow pains."""

    __tablename__ = "pain_clusters"

    cluster_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    cluster_theme: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    representative_problem_statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    cluster_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )


class ClusterMembershipORM(Base):
    """Map canonical records to clusters."""

    __tablename__ = "cluster_memberships"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    canonical_record_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    cluster_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    distance_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )


class FinalBusinessIntelligenceORM(Base):
    """Aggregated final business intelligence from clusters."""

    __tablename__ = "final_business_intelligence"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    cluster_theme: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    problem_statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    precise_description_of_the_problem: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    supporting_post_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    business_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    avg_frustration_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    affected_tools: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
    )

    possible_companies_affected: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
