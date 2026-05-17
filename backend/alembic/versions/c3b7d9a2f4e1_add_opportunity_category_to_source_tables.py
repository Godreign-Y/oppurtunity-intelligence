"""add opportunity category to source tables

Revision ID: c3b7d9a2f4e1
Revises: bdfbdd61de53
Create Date: 2026-05-17 21:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3b7d9a2f4e1"
down_revision: Union[str, None] = "bdfbdd61de53"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply schema upgrades."""
    op.add_column("hiring_signals", sa.Column("source_url", sa.Text(), nullable=True))
    op.add_column("hiring_signals", sa.Column("opportunity_category", sa.String(length=100), nullable=True))
    op.add_column("funding_events", sa.Column("opportunity_category", sa.String(length=100), nullable=True))
    op.add_column("github_signals", sa.Column("opportunity_category", sa.String(length=100), nullable=True))
    op.add_column("normalized_signals", sa.Column("opportunity_category", sa.String(length=100), nullable=True))

    op.execute(
        "UPDATE hiring_signals SET opportunity_category = 'DevOps Modernization' "
        "WHERE opportunity_category IS NULL"
    )
    op.execute(
        "UPDATE funding_events SET opportunity_category = 'Cloud Migration' "
        "WHERE opportunity_category IS NULL"
    )
    op.execute(
        "UPDATE github_signals SET opportunity_category = 'DevOps Modernization' "
        "WHERE opportunity_category IS NULL"
    )
    op.execute(
        "UPDATE normalized_signals SET opportunity_category = 'DevOps Modernization' "
        "WHERE opportunity_category IS NULL"
    )


def downgrade() -> None:
    """Revert schema upgrades."""
    op.drop_column("normalized_signals", "opportunity_category")
    op.drop_column("github_signals", "opportunity_category")
    op.drop_column("funding_events", "opportunity_category")
    op.drop_column("hiring_signals", "opportunity_category")
    op.drop_column("hiring_signals", "source_url")
