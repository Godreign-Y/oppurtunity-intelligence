"""Initial schema: companies and signals tables

Revision ID: 0001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create companies and signals tables."""

    op.create_table(
        "companies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("domain", sa.String(255), nullable=True),
        sa.Column("ats_platform", sa.String(50), nullable=True),
        sa.Column("blog_url", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_companies_name", "companies", ["name"])

    op.create_table(
        "signals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=True),
        sa.Column("technologies", JSON, nullable=True),
        sa.Column("topics", JSON, nullable=True),
        sa.Column("pain_indicators", JSON, nullable=True),
        sa.Column("business_implications", JSON, nullable=True),
        sa.Column("opportunity_mapping", JSON, nullable=True),
        sa.Column("confidence", sa.Float, default=0.0),
        sa.Column("evidence", JSON, nullable=True),
        sa.Column("source_url", sa.Text, nullable=True),
        sa.Column("ai_analysis", JSON, nullable=True),
        sa.Column("role_title", sa.String(255), nullable=True),
        sa.Column("department", sa.String(255), nullable=True),
        sa.Column("seniority", sa.String(100), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_signals_company_id", "signals", ["company_id"])


def downgrade() -> None:
    """Drop signals and companies tables."""
    op.drop_index("ix_signals_company_id", table_name="signals")
    op.drop_table("signals")
    op.drop_index("ix_companies_name", table_name="companies")
    op.drop_table("companies")
