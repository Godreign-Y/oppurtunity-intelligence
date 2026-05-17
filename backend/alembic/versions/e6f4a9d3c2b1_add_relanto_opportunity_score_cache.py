"""add relanto opportunity score cache

Revision ID: e6f4a9d3c2b1
Revises: d4a8e7b61c20
Create Date: 2026-05-17 23:20:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "e6f4a9d3c2b1"
down_revision: Union[str, None] = "d4a8e7b61c20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "relanto_opportunity_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("source_id", sa.String(length=100), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("opportunity_category", sa.String(length=100), nullable=True),
        sa.Column("confidence", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("priority", sa.String(length=50), nullable=False, server_default="Medium"),
        sa.Column("relanto_relevance_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("practices", sa.JSON(), nullable=True),
        sa.Column("past_deals", sa.JSON(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("technologies", sa.JSON(), nullable=True),
        sa.Column("pain_indicators", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source", "source_id", name="uq_relanto_opportunity_score_source"),
    )
    op.create_index("ix_relanto_scores_company", "relanto_opportunity_scores", ["company_name"])
    op.create_index("ix_relanto_scores_category", "relanto_opportunity_scores", ["opportunity_category"])
    op.create_index("ix_relanto_scores_fit", "relanto_opportunity_scores", ["relanto_relevance_score"])


def downgrade() -> None:
    op.drop_index("ix_relanto_scores_fit", table_name="relanto_opportunity_scores")
    op.drop_index("ix_relanto_scores_category", table_name="relanto_opportunity_scores")
    op.drop_index("ix_relanto_scores_company", table_name="relanto_opportunity_scores")
    op.drop_table("relanto_opportunity_scores")
